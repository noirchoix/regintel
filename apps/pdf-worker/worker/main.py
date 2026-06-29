import os
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


def _candidate_executables(name: str) -> list[str]:
    """Return executable candidates visible to this Python process.

    Windows GUI PATH edits are not always inherited by terminals/uvicorn processes
    that were already open.  This helper supports explicit env vars plus common
    install locations, so a correctly installed Tectonic/MiKTeX can still be found.
    """
    explicit_env = {
        'tectonic': ['TECTONIC_PATH', 'LATEX_ENGINE_PATH'],
        'pdflatex': ['PDFLATEX_PATH', 'MIKTEX_PDFLATEX_PATH'],
    }.get(name, [])

    candidates: list[str] = []
    for env_name in explicit_env:
        value = os.getenv(env_name)
        if value:
            candidates.append(value)

    found = shutil.which(name)
    if found:
        candidates.append(found)

    if os.name == 'nt':
        program_files = os.getenv('ProgramFiles', r'C:\Program Files')
        local_app_data = os.getenv('LOCALAPPDATA', '')
        candidates.extend([
            rf'{program_files}\tectonic\tectonic.exe',
            rf'{program_files}\Tectonic\tectonic.exe',
            rf'{program_files}\MiKTeX\miktex\bin\x64\pdflatex.exe',
            rf'{local_app_data}\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe',
        ])

    unique: list[str] = []
    for candidate in candidates:
        if candidate and candidate not in unique:
            unique.append(candidate)
    return unique


def _resolve_executable(name: str) -> str | None:
    for candidate in _candidate_executables(name):
        path = Path(candidate)
        if path.exists() and path.is_file():
            return str(path)
        # shutil.which can resolve bare names or PATH-visible commands.
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def _latex_diagnostics() -> str:
    path_value = os.getenv('PATH', '')
    return (
        'No LaTeX engine found by the PDF worker process. '
        'Install Tectonic or MiKTeX, then restart the terminal/uvicorn process, or set '
        'TECTONIC_PATH/LATEX_ENGINE_PATH to the full tectonic.exe path.\n\n'
        f'Worker PATH={path_value}\n'
        f'Tectonic candidates={_candidate_executables("tectonic")}\n'
        f'pdflatex candidates={_candidate_executables("pdflatex")}'
    )


def compile_tex_to_pdf(tex_path: str) -> Tuple[bool, str]:
    tex_file = Path(tex_path)
    workdir = tex_file.parent
    outdir = workdir

    tectonic = _resolve_executable('tectonic')
    pdflatex = _resolve_executable('pdflatex')

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
            return False, _latex_diagnostics()

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



@app.get('/health')
async def health() -> dict:
    return {
        'status': 'ok',
        'tectonic': _resolve_executable('tectonic'),
        'pdflatex': _resolve_executable('pdflatex'),
        'path': os.getenv('PATH', ''),
    }


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
