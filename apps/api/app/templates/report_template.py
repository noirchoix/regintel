from jinja2 import Template

TEMPLATE = r"""
\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage{hyperref}
\usepackage{longtable}
\title{Regulatory Assessment Report}
\date{\today}

\begin{document}
\maketitle

\section*{Product}
\textbf{Name:} {{ assessment.product_name }} \\
\textbf{Company:} {{ assessment.company_name or "N/A" }} \\
\textbf{Jurisdiction:} {{ assessment.jurisdiction }} \\

\section*{Classification}
{{ result.classification }}

\section*{Confidence Band}
{{ result.confidence_band }}

\section*{Applicable Standards}
\begin{itemize}
{% for standard in result.standards %}
\item {{ standard }}
{% endfor %}
\end{itemize}

\section*{Executive Summary}
{{ result.explanation.executive_summary }}

\section*{Triggered Rules}
\begin{longtable}{p{0.2\linewidth} p{0.2\linewidth} p{0.5\linewidth}}
\textbf{Rule ID} & \textbf{Outcome} & \textbf{Rationale} \\
{% for rule in result.triggered_rules %}
{{ rule.rule_id }} & {{ rule.outcome }} & {{ rule.rationale }} \\
{% endfor %}
\end{longtable}

\section*{Evidence}
\begin{longtable}{p{0.2\linewidth} p{0.2\linewidth} p{0.5\linewidth}}
\textbf{Framework} & \textbf{Citation} & \textbf{Excerpt} \\
{% for item in result.evidence %}
{{ item.framework }} & {{ item.citation }} & {{ item.excerpt }} \\
{% endfor %}
\end{longtable}

\section*{Assumptions}
\begin{itemize}
{% for assumption in result.explanation.assumptions %}
\item {{ assumption }}
{% endfor %}
\end{itemize}

\section*{Open Questions}
\begin{itemize}
{% for question in result.explanation.unresolved_questions %}
\item {{ question }}
{% endfor %}
\end{itemize}

\section*{Recommended Next Steps}
\begin{itemize}
{% for step in result.explanation.next_steps %}
\item {{ step }}
{% endfor %}
\end{itemize}

\end{document}
"""


def render_latex(assessment, result: dict) -> str:
    template = Template(TEMPLATE)
    return template.render(assessment=assessment, result=result)
