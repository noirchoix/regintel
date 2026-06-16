from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.models.assessment import Assessment, AssessmentResult
from app.schemas.assessment import AssessmentCreate, AssessmentResponse, AssessmentResultPayload
from app.services.assessment import evaluate_assessment, serialize_assessment_response

router = APIRouter()


@router.post('', response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assessment(
    payload: AssessmentCreate,
    db: Session = Depends(db_session),
) -> AssessmentResponse:
    assessment = Assessment(
        owner_id=None,
        product_name=payload.profile.product_name,
        company_name=payload.profile.company_name,
        jurisdiction=payload.jurisdiction,
        payload=payload.model_dump(mode='json'),
        status='processing',
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    result_payload = await evaluate_assessment(payload)
    result = AssessmentResult(
        assessment_id=assessment.id,
        classification=result_payload.classification,
        confidence_band=result_payload.confidence_band,
        summary=result_payload.model_dump(mode='json'),
    )
    assessment.status = 'completed'
    db.add(result)
    db.commit()
    db.refresh(assessment)

    return serialize_assessment_response(assessment, result_payload)


@router.get('', response_model=list[AssessmentResponse])
async def list_assessments(
    db: Session = Depends(db_session),
) -> list[AssessmentResponse]:
    assessments = db.query(Assessment).order_by(Assessment.created_at.desc()).limit(50).all()
    responses = []
    for assessment in assessments:
        result_payload = AssessmentResultPayload.model_validate(assessment.result.summary) if assessment.result else None
        responses.append(serialize_assessment_response(assessment, result_payload))
    return responses


@router.get('/{assessment_id}', response_model=AssessmentResponse)
async def get_assessment(
    assessment_id: str,
    db: Session = Depends(db_session),
) -> AssessmentResponse:
    assessment = db.get(Assessment, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail='Assessment not found')

    result_payload = AssessmentResultPayload.model_validate(assessment.result.summary) if assessment.result else None
    return serialize_assessment_response(assessment, result_payload)