from datetime import datetime

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.core.config import settings
from app.models.assessment import Assessment, ReportArtifact
from app.schemas.assessment import AssessmentResultPayload
from app.schemas.report import ReportRequest, ReportResponse
from app.services.reporting import render_report_latex

router = APIRouter()


@router.post('', response_model=ReportResponse)
async def generate_report(
    payload: ReportRequest,
    db: Session = Depends(db_session),
) -> ReportResponse:
    assessment = db.get(Assessment, payload.assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail='Assessment not found')
    if not assessment.result:
        raise HTTPException(status_code=400, detail='Assessment has no computed result')

    result_payload = AssessmentResultPayload.model_validate(assessment.result.summary)
    latex = render_report_latex(
        assessment_id=assessment.id,
        product_name=assessment.product_name,
        jurisdiction=assessment.jurisdiction,
        result=result_payload,
    )

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f'{settings.pdf_worker_url}/render',
                json={
                    'assessment_id': assessment.id,
                    'latex_source': latex
                }
            )
            response.raise_for_status()
            render_result = response.json()
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail=f'PDF worker is unreachable at {settings.pdf_worker_url}. Start the PDF worker or correct PDF_WORKER_URL.'
        )
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text if exc.response is not None else 'PDF worker returned an error.'
        raise HTTPException(status_code=502, detail=f'PDF worker error: {detail}')
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'Unexpected report generation error: {exc}')

    artifact = ReportArtifact(
        assessment_id=assessment.id,
        format='pdf',
        status=render_result.get('status', 'completed'),
        storage_url=render_result.get('download_url'),
        latex_source=latex,
        manifest=render_result,
        created_at=datetime.utcnow(),
    )
    db.add(artifact)
    db.commit()
    db.refresh(artifact)

    return ReportResponse(
        artifact_id=artifact.id,
        format=artifact.format,
        storage_url=artifact.storage_url,
        created_at=artifact.created_at,
        status=artifact.status,
    )