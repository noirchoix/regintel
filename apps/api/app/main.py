from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.session import init_db
from app.services.qdrant_store import QdrantStore


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    init_db()
    QdrantStore().ensure_collection()
    yield


app = FastAPI(
    title=settings.app_name,
    version='1.1.0',
    openapi_url=f'{settings.api_prefix}/openapi.json',
    docs_url=f'{settings.api_prefix}/docs',
    redoc_url=f'{settings.api_prefix}/redoc',
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(api_router, prefix=settings.api_prefix)


@app.get('/')
async def root() -> dict[str, str]:
    return {'service': settings.app_name, 'status': 'ok'}
