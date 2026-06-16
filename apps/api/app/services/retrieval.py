from app.schemas.assessment import EvidenceSnippet, ProductProfile
from app.services.embeddings import EmbeddingService
from app.services.qdrant_store import QdrantStore


async def retrieve_evidence(profile: ProductProfile, standards: list[str], jurisdiction: str | None = None) -> list[EvidenceSnippet]:
    query = ' '.join([
        profile.product_name,
        profile.intended_use,
        'clinical decision support' if profile.clinical_decision_support else '',
        'diagnosis' if profile.provides_diagnosis else '',
        'treatment recommendation' if profile.provides_treatment_recommendation else '',
        'PHI EHR privacy security' if (profile.stores_phi or profile.integrates_with_ehr) else '',
    ]).strip()

    embedder = EmbeddingService()
    store = QdrantStore()
    store.ensure_collection()
    hits = store.search(embedder.embed_query(query), jurisdiction=jurisdiction, frameworks=standards, limit=8)

    evidence: list[EvidenceSnippet] = []
    for hit in hits:
        payload = hit.payload or {}
        evidence.append(
            EvidenceSnippet(
                source_id=str(payload.get('chunk_id') or payload.get('document_id') or hit.id),
                framework=str(payload.get('framework', 'Unknown')),
                citation=str(payload.get('citation', payload.get('title', 'Unknown source'))),
                excerpt=str(payload.get('text', '')),
                score=float(hit.score or 0.0),
                metadata={
                    'jurisdiction': payload.get('jurisdiction'),
                    'version': payload.get('version'),
                    'document_id': payload.get('document_id'),
                },
            )
        )
    return evidence
