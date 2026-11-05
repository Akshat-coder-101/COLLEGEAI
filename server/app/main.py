import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.session import engine, Base
from app.api.routes import health, research, documents, discoveries, experiments, projects

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure database tables are created
    logger.info("Initializing database schemas...")
    Base.metadata.create_all(bind=engine)
    logger.info("HypothesisLab AI backend ready.")
    yield
    # Shutdown
    logger.info("HypothesisLab AI backend shutting down.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Autonomous multi-agent research and discovery platform backend. "
        "Enables evidence-backed scientific discovery, cross-domain connection detection, "
        "hypothesis synthesis, critical review, and isolated computational simulation."
    ),
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes under Base URL /api/v1
api_v1_router = FastAPI()
app.include_router(health.router, prefix=settings.API_V1_STR)
app.include_router(projects.router, prefix=settings.API_V1_STR)
app.include_router(research.router, prefix=settings.API_V1_STR)
app.include_router(documents.router, prefix=settings.API_V1_STR)
app.include_router(discoveries.router, prefix=settings.API_V1_STR)
app.include_router(experiments.router, prefix=settings.API_V1_STR)

# Also expose direct /health for root health checkers
app.include_router(health.router)


@app.get("/")
def root():
    return {
        "product": settings.PROJECT_NAME,
        "version": "1.0.0",
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR,
        "status": "operational"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
