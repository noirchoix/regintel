from app.schemas.assessment import EvidenceSnippet


async def generate_explanation(*, profile, classification: str, standards: list[str], rules, evidence: list[EvidenceSnippet], assumptions: list[str], unresolved_questions: list[str]) -> dict:
    top_evidence = '; '.join(f'{item.framework}: {item.citation}' for item in evidence[:3]) if evidence else 'No supporting citations retrieved yet.'
    return {
        'executive_summary': (
            f"{profile.product_name} is provisionally classified as '{classification}'. "
            f"The rules engine triggered {len(rules)} decision nodes and mapped the product to {', '.join(standards)}. "
            f"Top supporting evidence: {top_evidence}"
        ),
        'assumptions': assumptions,
        'unresolved_questions': unresolved_questions,
        'next_steps': [
            'Validate intended use wording against marketing and design inputs.',
            'Confirm clinical workflow, user role, and degree of human oversight.',
            'Generate a versioned regulatory report for design control records.',
        ],
    }
