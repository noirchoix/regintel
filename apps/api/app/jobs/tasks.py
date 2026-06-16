from datetime import datetime

from app.db.session import SessionLocal
from app.models.assessment import IngestionJob, StandardDocument
from app.services.document_parser import DocumentParser, chunk_text
from app.services.embeddings import EmbeddingService
from app.services.qdrant_store import QdrantStore


def ingest_standard_document(job_id: str) -> None:
    db = SessionLocal()
    try:
        job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
        if not job:
            return
        document = db.query(StandardDocument).filter(StandardDocument.id == job.document_id).first()
        if not document:
            job.status = 'failed'
            job.error_message = 'Document not found'
            db.commit()
            return

        job.status = 'running'
        document.status = 'processing'
        db.commit()

        text = DocumentParser.parse(document.storage_path)
        chunks = chunk_text(text)
        embeddings = EmbeddingService().embed_texts(chunks)
        store = QdrantStore()
        store.ensure_collection()
        payloads = []
        for idx, (chunk, vector) in enumerate(zip(chunks, embeddings), start=1):
            payloads.append({
                'vector': vector,
                'payload': {
                    'chunk_id': f'{document.id}:{idx}',
                    'document_id': document.id,
                    'framework': document.framework,
                    'jurisdiction': document.jurisdiction,
                    'version': document.version,
                    'title': document.title,
                    'citation': f"{document.framework} {document.version} chunk {idx}",
                    'text': chunk,
                },
            })
        store.upsert_chunks(payloads)

        document.status = 'indexed'
        document.chunk_count = len(chunks)
        job.status = 'completed'
        job.completed_at = datetime.utcnow()
        db.commit()
    except Exception as exc:
        db.rollback()
        job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
        if job:
            job.status = 'failed'
            job.error_message = str(exc)
            db.commit()
        raise
    finally:
        db.close()
