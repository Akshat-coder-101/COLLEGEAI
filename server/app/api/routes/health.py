from fastapi import APIRouter
from app.config import settings
from app.services.rate_limiter import global_rate_limiter

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
        "rate_limiting": {
            "max_rpm_per_model": settings.MAX_RPM_PER_MODEL,
            "max_rpd_per_model": settings.MAX_RPD_PER_MODEL,
            "spacing_delay_seconds": settings.REQUEST_DELAY_SECONDS,
            "model_routing": {
                "planner": settings.MODEL_PLANNER,
                "analyzer": settings.MODEL_ANALYZER,
                "cross_domain": settings.MODEL_CROSS_DOMAIN,
                "gap_detection": settings.MODEL_GAP_DETECTION,
                "hypothesis": settings.MODEL_HYPOTHESIS,
                "reviewer": settings.MODEL_REVIEWER,
                "simulation": settings.MODEL_SIMULATION,
            },
            "active_quotas": global_rate_limiter.get_stats()
        }
    }
