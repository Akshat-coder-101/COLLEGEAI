from fastapi import APIRouter
from app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "database": "connected",
        "gemini_api_configured": bool(settings.GEMINI_API_KEY),
        "semantic_scholar_configured": bool(settings.SEMANTIC_SCHOLAR_API_KEY),
        "github_configured": bool(settings.GITHUB_TOKEN),
    }
