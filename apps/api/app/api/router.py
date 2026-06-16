from fastapi import APIRouter

from app.api.routes import assessments, auth, health, reports, standards

api_router = APIRouter()
api_router.include_router(health.router, tags=['health'])
# api_router.include_router(auth.router, prefix='/auth', tags=['auth'])
api_router.include_router(assessments.router, prefix='/assessments', tags=['assessments'])
api_router.include_router(reports.router, prefix='/reports', tags=['reports'])
api_router.include_router(standards.router, prefix='/standards', tags=['standards'])
