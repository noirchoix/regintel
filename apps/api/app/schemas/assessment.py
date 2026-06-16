from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class ProductProfile(BaseModel):
    product_name: str = Field(min_length=2, max_length=255)
    company_name: str | None = Field(default=None, max_length=255)
    intended_use: str = Field(min_length=10)
    target_users: list[str] = Field(default_factory=list)
    jurisdictions: list[str] = Field(default_factory=lambda: ['US'])
    delivery_model: Literal['web', 'mobile', 'desktop', 'embedded', 'api', 'mixed'] = 'web'
    clinical_decision_support: bool = False
    provides_diagnosis: bool = False
    provides_treatment_recommendation: bool = False
    stores_phi: bool = False
    integrates_with_ehr: bool = False
    uses_ml_models: bool = True
    human_in_the_loop: bool = True
    software_lifecycle_stage: Literal['idea', 'design', 'prototype', 'pre-market', 'market'] = 'idea'


class AssessmentCreate(BaseModel):
    jurisdiction: str = Field(default='US', min_length=2, max_length=16)
    profile: ProductProfile


class TriggeredRule(BaseModel):
    rule_id: str
    title: str
    outcome: str
    rationale: str
    severity: Literal['info', 'review', 'high'] = 'info'


class EvidenceSnippet(BaseModel):
    source_id: str
    framework: str
    citation: str
    excerpt: str
    score: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class AssessmentExplanation(BaseModel):
    executive_summary: str
    assumptions: list[str] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)


class AssessmentResultPayload(BaseModel):
    classification: str
    confidence_band: Literal['low', 'medium', 'high']
    standards: list[str] = Field(default_factory=list)
    triggered_rules: list[TriggeredRule] = Field(default_factory=list)
    evidence: list[EvidenceSnippet] = Field(default_factory=list)
    explanation: AssessmentExplanation


class AssessmentResponse(BaseModel):
    id: str
    status: str
    jurisdiction: str
    product_name: str
    created_at: datetime
    result: AssessmentResultPayload | None = None
