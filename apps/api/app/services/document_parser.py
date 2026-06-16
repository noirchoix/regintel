from pathlib import Path

from pypdf import PdfReader


class DocumentParser:
    @staticmethod
    def parse(path: str) -> str:
        file_path = Path(path)
        suffix = file_path.suffix.lower()
        if suffix == '.pdf':
            reader = PdfReader(str(file_path))
            return '\n'.join(page.extract_text() or '' for page in reader.pages)
        return file_path.read_text(encoding='utf-8', errors='ignore')


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 150) -> list[str]:
    cleaned = ' '.join(text.split())
    if not cleaned:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(cleaned):
        end = min(len(cleaned), start + chunk_size)
        chunks.append(cleaned[start:end])
        if end == len(cleaned):
            break
        start = max(0, end - overlap)
    return chunks
