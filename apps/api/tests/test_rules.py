from app.schemas.assessment import ProductProfile
from app.services.rules import evaluate_rules


def test_rule_engine_sets_samd_classification():
    profile = ProductProfile(
        product_name="DentalVision AI",
        intended_use="Analyze dental images to assist diagnosis of oral disease.",
        provides_diagnosis=True,
        clinical_decision_support=True,
        stores_phi=True,
        uses_ml_models=True,
    )
    outcome = evaluate_rules(profile, "US")
    assert "Potential SaMD" in outcome.classification
    assert any(rule.rule_id == "MD_CLASSIFICATION_001" for rule in outcome.triggered_rules)
