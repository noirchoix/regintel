# Regulatory Intelligence Engine

Production-grade monorepo for a regulatory intelligence platform for medical software startups.

## Implemented capabilities
- FastAPI API with JWT auth and role-based access control
- PostgreSQL persistence for users, assessments, reports, standards, and ingestion jobs
- Live Qdrant retrieval pipeline with Dockerized Qdrant
- Voyage embeddings with deterministic local fallback for development
- Background ingestion jobs via Redis + RQ worker
- Standards ingestion admin endpoints for upload, indexing, and job monitoring
- SvelteKit workbench UI
- Dedicated PDF worker with Tectonic-based LaTeX compilation

## Roles
- `admin`: full access, upload/index standards, list all assessments
- `reviewer`: upload/index standards, review all assessments
- `analyst`: run and view own assessments
- `viewer`: read-only access where enabled

## Default credentials
- Email: `admin@regintel.local`
- Password: `Admin123!`

Change them before any real deployment.

## Local Docker workflow
From `infrastructure/docker`:

```bash
docker compose up --build
```

Services:
- API: `http://localhost:8000`
- API docs: `http://localhost:8000/v1/docs`
- Web: `http://localhost:5173`
- PDF worker: `http://localhost:8010`
- Qdrant: `http://localhost:6333/dashboard`

## Standards ingestion flow
1. Sign in as an admin.
2. POST a file to `/v1/standards/admin/upload` with `title`, `framework`, `jurisdiction`, `version`, and `file`.
3. API persists the document and enqueues an ingestion job.
4. RQ worker parses the file, chunks text, generates embeddings, and upserts points into Qdrant.
5. Assessments use those live Qdrant citations during evidence retrieval.

## PDF reporting flow
1. API renders deterministic LaTeX from the stored assessment result.
2. PDF worker writes a `.tex` file.
3. Worker compiles via Tectonic or `pdflatex` fallback.
4. API stores artifact metadata and returns the download URL.
