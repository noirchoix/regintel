from textwrap import shorten

from jinja2 import Template

from app.schemas.assessment import AssessmentResultPayload


def tex_compact(value: str | None, *, limit: int | None = None) -> str:
    if value is None:
        return ""
    cleaned = " ".join(str(value).split())
    if limit and len(cleaned) > limit:
        return shorten(cleaned, width=limit, placeholder="...")
    return cleaned


def tex_escape(value: str | None) -> str:
    if value is None:
        return ""
    value = tex_compact(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return value


def render_itemize(items) -> str:
    if not items:
        return r"\textit{None recorded.}" + "\n"
    lines = [r"\begin{itemize}[leftmargin=1.25em,itemsep=0.25em,topsep=0.25em]"]
    for item in items:
        lines.append(f"\\item {tex_escape(item)}")
    lines.append(r"\end{itemize}")
    return "\n".join(lines)


def render_triggered_rules_block(triggered_rules) -> str:
    if not triggered_rules:
        return r"\textit{No triggered rules.}" + "\n"

    lines = []

    for rule in triggered_rules:
        lines.extend([
            r"\begin{samepage}",
            r"\noindent\begin{minipage}{\linewidth}",
            f"\\textbf{{{tex_escape(rule.rule_id)}}} "
            f"\\hfill \\riskbadge{{{tex_escape(rule.severity).upper()}}}\\\\",
            f"\\textit{{{tex_escape(rule.title)}}}\\\\[0.25em]",
            f"{tex_escape(rule.rationale)}",
            r"\end{minipage}",
            r"\vspace{0.85em}",
            r"\end{samepage}",
        ])

    return "\n".join(lines)


def render_evidence_block(evidence) -> str:
    if not evidence:
        return r"\textit{No evidence retrieved.}" + "\n"

    lines = []

    for index, item in enumerate(evidence, start=1):
        excerpt = tex_escape(tex_compact(item.excerpt, limit=900))
        score = f"{float(item.score):.3f}" if item.score is not None else "N/A"
        lines.extend([
            r"\begin{samepage}",
            r"\noindent\begin{minipage}{\linewidth}",
            f"\\textbf{{Evidence {index}. {tex_escape(item.framework)}}} "
            f"\\hfill \\textcolor{{muted}}{{Score {score}}}\\\\",
            f"\\textcolor{{muted}}{{{tex_escape(item.citation)}}}\\\\[0.35em]",
            excerpt,
            r"\end{minipage}",
            r"\vspace{0.9em}",
            r"\end{samepage}",
        ])

    return "\n".join(lines)


REPORT_TEMPLATE = Template("""
\\documentclass{article}
\\usepackage[utf8]{inputenc}
\\usepackage[T1]{fontenc}
\\usepackage{geometry}
\\usepackage{array}
\\usepackage{xcolor}
\\usepackage{enumitem}
\\usepackage{hyperref}
\\geometry{margin=0.85in}
\\definecolor{accent}{HTML}{1D4ED8}
\\definecolor{muted}{HTML}{64748B}
\\definecolor{ruleline}{HTML}{CBD5E1}
\\hypersetup{colorlinks=true, linkcolor=accent, urlcolor=accent}
\\setlength{\\parindent}{0pt}
\\setlength{\\parskip}{0.65em}
\\setlist{nosep}
\\renewcommand{\\arraystretch}{1.25}
\\newcommand{\\sectionrule}{\\vspace{-0.35em}\\noindent{\\color{ruleline}\\rule{\\linewidth}{0.4pt}}\\vspace{0.45em}}
{% raw %}\\newcommand{\\riskbadge}[1]{\\textcolor{accent}{\\footnotesize\\textbf{#1}}}{% endraw %}
\\begin{document}

{\\LARGE\\textbf{Regulatory Assessment Report}}\\\\[-0.1em]
{\\textcolor{muted}{Generated classification summary and evidence trace.}}
\\vspace{0.75em}
\\sectionrule

\\textbf{Assessment ID:} {{ assessment_id }}\\\\
\\textbf{Product:} {{ product_name }}\\\\
\\textbf{Jurisdiction:} {{ jurisdiction }}\\\\
\\textbf{Classification:} {{ classification }}\\\\
\\textbf{Confidence:} {{ confidence_band }}

\\subsection*{Triggered Standards}
\\sectionrule
{{ triggered_standards_block }}

\\subsection*{Executive Summary}
\\sectionrule
{{ executive_summary }}

\\subsection*{Triggered Rules}
\\sectionrule
{{ triggered_rules_block }}

\\subsection*{Evidence Trace}
\\sectionrule
{{ evidence_trace_block }}

\\subsection*{Open Questions}
\\sectionrule
{{ open_questions_block }}

\\end{document}
""")


def render_report_latex(
    *,
    assessment_id: str,
    product_name: str,
    jurisdiction: str,
    result: AssessmentResultPayload,
) -> str:
    explanation = result.explanation

    return REPORT_TEMPLATE.render(
        assessment_id=tex_escape(assessment_id),
        product_name=tex_escape(product_name),
        jurisdiction=tex_escape(jurisdiction),
        classification=tex_escape(result.classification),
        confidence_band=tex_escape(result.confidence_band),
        executive_summary=tex_escape(
            explanation.executive_summary if explanation and explanation.executive_summary else "No executive summary available."
        ),
        triggered_standards_block=render_itemize(getattr(result, "standards", []) or []),
        triggered_rules_block=render_triggered_rules_block(getattr(result, "triggered_rules", []) or []),
        evidence_trace_block=render_evidence_block(getattr(result, "evidence", []) or []),
        open_questions_block=render_itemize(
            getattr(explanation, "unresolved_questions", []) if explanation else []
        ),
    )
