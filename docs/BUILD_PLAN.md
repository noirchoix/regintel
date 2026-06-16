# Build status

The scaffold has been upgraded to include:
- production-oriented auth and RBAC
- live document ingestion with Qdrant indexing
- background jobs for indexing
- full PDF compilation worker using Tectonic
- Docker compose orchestration for local production-like development

## Remaining hardening before regulated production use
- external object storage for uploads and artifacts
- audit trail signatures and immutable event log
- richer admin UI routes in SvelteKit
- document OCR and richer parser support for scans/Word docs
- monitoring dashboards and alert policies
- full migration management with Alembic
