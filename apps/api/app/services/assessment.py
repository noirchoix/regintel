from app.schemas.assessment import AssessmentCreate, AssessmentExplanation, AssessmentResponse, AssessmentResultPayload
from app.services.llm import generate_explanation
from app.services.retrieval import retrieve_evidence
from app.services.rules import evaluate_rules


async def evaluate_assessment(payload: AssessmentCreate) -> AssessmentResultPayload:
    rule_outcome = evaluate_rules(payload.profile, payload.jurisdiction)
    evidence = await retrieve_evidence(payload.profile, rule_outcome.standards, payload.jurisdiction)
    explanation = await generate_explanation(
        profile=payload.profile,
        classification=rule_outcome.classification,
        standards=rule_outcome.standards,
        rules=rule_outcome.triggered_rules,
        evidence=evidence,
        assumptions=rule_outcome.assumptions,
        unresolved_questions=rule_outcome.unresolved_questions,
    )
    confidence = 'high' if evidence and len(rule_outcome.triggered_rules) >= 2 else 'medium' if evidence else 'low'
    return AssessmentResultPayload(
        classification=rule_outcome.classification,
        confidence_band=confidence,
        standards=rule_outcome.standards,
        triggered_rules=rule_outcome.triggered_rules,
        evidence=evidence,
        explanation=AssessmentExplanation.model_validate(explanation),
    )


def serialize_assessment_response(assessment, result_payload: AssessmentResultPayload | None) -> AssessmentResponse:
    return AssessmentResponse(
        id=assessment.id,
        status=assessment.status,
        jurisdiction=assessment.jurisdiction,
        product_name=assessment.product_name,
        created_at=assessment.created_at,
        result=result_payload,
    )
