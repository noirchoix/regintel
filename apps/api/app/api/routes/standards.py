from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_current_user, require_roles
from app.core.config import settings
from app.jobs.queue import get_queue
from app.models.assessment import IngestionJob, StandardDocument, User
from app.schemas.assessment import EvidenceSnippet
from app.schemas.standards import IngestionJobRead, SearchRequest, StandardDocumentRead
from app.services.embeddings import EmbeddingService
from app.services.qdrant_store import QdrantStore

router = APIRouter()


@router.post('/admin/upload', response_model=IngestionJobRead, status_code=status.HTTP_201_CREATED)
async def upload_standard(
    title: str = Form(...),
    framework: str = Form(...),
    jurisdiction: str = Form(...),
    version: str = Form('latest'),
    file: UploadFile = File(...),
    db: Session = Depends(db_session),
    _: User = Depends(require_roles('admin', 'reviewer')),
) -> IngestionJobRead:
    suffix = Path(file.filename).suffix or '.txt'
    path = settings.uploads_path / f'{uuid4().hex}{suffix}'
    path.write_bytes(await file.read())

    document = StandardDocument(
        title=title,
        framework=framework,
        jurisdiction=jurisdiction,
        version=version,
        source_filename=file.filename,
        storage_path=str(path),
        metadata_json={},
        status='uploaded',
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    job = IngestionJob(document_id=document.id, status='queued')
    db.add(job)
    db.commit()
    db.refresh(job)

    get_queue().enqueue('app.jobs.tasks.ingest_standard_document', job.id)
    return IngestionJobRead.model_validate(job, from_attributes=True)


@router.get('/admin/documents', response_model=list[StandardDocumentRead])
async def list_documents(db: Session = Depends(db_session), _: User = Depends(require_roles('admin', 'reviewer'))):
    docs = db.query(StandardDocument).order_by(StandardDocument.created_at.desc()).all()
    return [StandardDocumentRead.model_validate(doc, from_attributes=True) for doc in docs]


@router.get('/admin/jobs', response_model=list[IngestionJobRead])
async def list_jobs(db: Session = Depends(db_session), _: User = Depends(require_roles('admin', 'reviewer'))):
    jobs = db.query(IngestionJob).order_by(IngestionJob.enqueued_at.desc()).all()
    return [IngestionJobRead.model_validate(job, from_attributes=True) for job in jobs]


@router.post('/search', response_model=list[EvidenceSnippet])
async def semantic_search(payload: SearchRequest, user: User = Depends(get_current_user)) -> list[EvidenceSnippet]:
    _ = user
    store = QdrantStore()
    store.ensure_collection()
    hits = store.search(EmbeddingService().embed_query(payload.query), jurisdiction=payload.jurisdiction, frameworks=payload.frameworks or None, limit=payload.limit)
    return [
        EvidenceSnippet(
            source_id=str(hit.payload.get('chunk_id', hit.id)),
            framework=str(hit.payload.get('framework', 'Unknown')),
            citation=str(hit.payload.get('citation', 'Unknown citation')),
            excerpt=str(hit.payload.get('text', '')),
            score=float(hit.score or 0.0),
            metadata={'document_id': hit.payload.get('document_id'), 'jurisdiction': hit.payload.get('jurisdiction'), 'version': hit.payload.get('version')},
        )
        for hit in hits
    ]
