import shutil
import subprocess
from pathlib import Path
from typing import Tuple
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from jinja2 import Template
from pydantic import BaseModel

from worker.config import settings

app = FastAPI(title=settings.worker_name)
OUTPUT_DIR = settings.output_path


class RenderRequest(BaseModel):
    assessment_id: str
    latex_source: str


# ---------- LaTeX helpers (from your templating/tectonic idea) ----------

def _tectonic_supports_new_cli(tectonic_path: str) -> bool:
    try:
        help_out = subprocess.run(
            [tectonic_path, '-X', 'compile', '--help'],
            capture_output=True, text=True, check=False,
        ).stdout.lower()
        return '--outdir' in help_out
    except Exception:
        return False


def compile_tex_to_pdf(tex_path: str) -> Tuple[bool, str]:
    tex_file = Path(tex_path)
    workdir = tex_file.parent
    outdir = workdir

    tectonic = shutil.which('tectonic')
    pdflatex = shutil.which('pdflatex')

    try:
        if tectonic:
            if _tectonic_supports_new_cli(tectonic):
                cmd = [
                    tectonic,
                    '-X',
                    'compile',
                    '--outdir',
                    str(outdir),
                    '--keep-intermediates',
                    '--keep-logs',
                    str(tex_file),
                ]
            else:
                cmd = [tectonic, '-o', str(outdir), str(tex_file)]
            proc = subprocess.run(cmd, cwd=str(workdir), capture_output=True, text=True)
        elif pdflatex:
            cmd = [
                pdflatex,
                '-interaction=nonstopmode',
                '-halt-on-error',
                '-output-directory',
                str(outdir),
                str(tex_file),
            ]
            proc = subprocess.run(cmd, cwd=str(workdir), capture_output=True, text=True)
        else:
            return False, 'No LaTeX engine found on PATH. Install Tectonic or MiKTeX.'

        if proc.returncode != 0:
            return False, (proc.stdout or '') + '\n' + (proc.stderr or '')

        pdf_guess = workdir / (tex_file.stem + '.pdf')
        if pdf_guess.exists():
            return True, str(pdf_guess)

        pdf_alt = Path(str(tex_file).replace('.tex', '.pdf'))
        if pdf_alt.exists():
            return True, str(pdf_alt)

        return False, 'Compilation reported success but PDF not found.'
    except Exception as e:
        return False, f'Exception during LaTeX compile: {e}'


def write_latex_math_proof(body: str, prefix: str, title: str) -> Path:
    template_str = r"""
\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{amsmath, amssymb, amsthm}
\usepackage{geometry}
\geometry{margin=1in}

\begin{document}
\section*{Mathematical Treatment of {{ title }}}

{{ body }}

\end{document}
"""
    t = Template(template_str)
    tex_content = t.render(title=title, body=body)
    tex_path = OUTPUT_DIR / f'{prefix}.tex'
    tex_path.write_text(tex_content, encoding='utf-8')
    return tex_path


def write_latex_research_summary(body: str, prefix: str, title: str) -> Path:
    template_str = r"""
\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{geometry}
\geometry{margin=1in}

\begin{document}
\section*{Research Summary: {{ title }}}

{{ body }}

\end{document}
"""
    t = Template(template_str)
    tex_content = t.render(title=title, body=body)
    tex_path = OUTPUT_DIR / f'{prefix}.tex'
    tex_path.write_text(tex_content, encoding='utf-8')
    return tex_path


def write_report_tex(source: str, prefix: str) -> Path:
    tex_path = OUTPUT_DIR / f'{prefix}.tex'
    tex_path.write_text(source, encoding='utf-8')
    return tex_path


@app.post('/render')
async def render_pdf(payload: RenderRequest) -> dict:
    prefix = f'{payload.assessment_id}-{uuid4().hex[:8]}'
    tex_path = write_report_tex(payload.latex_source, prefix)
    ok, result = compile_tex_to_pdf(str(tex_path))
    if not ok:
        raise HTTPException(status_code=500, detail=result)
    pdf_path = Path(result)
    return {
        'status': 'completed',
        'download_url': f'{settings.public_base_url}/{pdf_path.name}',
        'artifact_path': str(pdf_path),
        'tex_path': str(tex_path),
    }


@app.get('/artifacts/{filename}')
async def get_artifact(filename: str):
    path = OUTPUT_DIR / filename
    return FileResponse(path)
