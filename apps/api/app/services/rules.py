from dataclasses import dataclass, field

from app.schemas.assessment import ProductProfile, TriggeredRule


@dataclass
class RuleOutcome:
    classification: str
    standards: list[str]
    triggered_rules: list[TriggeredRule] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    unresolved_questions: list[str] = field(default_factory=list)


def evaluate_rules(profile: ProductProfile, jurisdiction: str) -> RuleOutcome:
    rules: list[TriggeredRule] = []
    standards = ['IEC 62304', 'ISO 13485']
    classification = 'Low Risk / Non-Device Review Required'
    assumptions: list[str] = []
    unresolved: list[str] = []

    if profile.provides_diagnosis or 'diagnos' in profile.intended_use.lower():
        classification = 'Potential SaMD / Medical Device'
        rules.append(TriggeredRule(rule_id='MD_CLASSIFICATION_001', title='Diagnostic intent', outcome='triggered', rationale='Product claims diagnostic intent or outputs diagnostic conclusions.', severity='high'))
        standards.append('FDA SaMD Guidance')

    if profile.clinical_decision_support:
        rules.append(TriggeredRule(rule_id='CDS_OVERSIGHT_001', title='Clinical decision support oversight', outcome='review', rationale='Clinical decision support functionality requires workflow and transparency review.', severity='review'))
        standards.append('FDA CDS Guidance')

    if profile.uses_ml_models:
        rules.append(TriggeredRule(rule_id='ML_CHANGE_001', title='ML-enabled functionality', outcome='review', rationale='ML-enabled functionality triggers model governance, monitoring, and change control expectations.', severity='review'))
        standards.append('GMLP Guidance')

    if profile.stores_phi or profile.integrates_with_ehr:
        rules.append(TriggeredRule(rule_id='DATA_PRIVACY_001', title='PHI/EHR handling', outcome='triggered', rationale='System processes PHI or EHR data and needs privacy/security controls.', severity='high'))
        standards.append('HIPAA Security Rule')

    if not profile.human_in_the_loop and (profile.provides_diagnosis or profile.provides_treatment_recommendation):
        classification = 'Elevated Risk SaMD Review'
        rules.append(TriggeredRule(rule_id='HUMAN_OVERSIGHT_001', title='Limited human oversight', outcome='high', rationale='Diagnostic or treatment outputs without sufficient human review increase regulatory risk.', severity='high'))

    if profile.software_lifecycle_stage in {'idea', 'design'}:
        assumptions.append('Lifecycle controls are not yet formally implemented.')
        unresolved.append('Confirm intended clinical claim language for marketing and product requirements.')

    deduped: list[str] = []
    for item in standards:
        if item not in deduped:
            deduped.append(item)

    return RuleOutcome(
        classification=classification,
        standards=deduped,
        triggered_rules=rules,
        assumptions=assumptions,
        unresolved_questions=unresolved,
    )
