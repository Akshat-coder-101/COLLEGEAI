import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure server is on sys.path
server_dir = Path(__file__).resolve().parent.parent
if str(server_dir) not in sys.path:
    sys.path.insert(0, str(server_dir))

from app.database.session import Base, get_db
import app.models.entities  # Ensure all model tables are registered in Base.metadata
from app.config import settings
from app.main import app
from app.services.llm_service import MockLLMProvider

TEST_DATABASE_URL = "sqlite:///./test_hypothesis_lab.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


import app.database.session as app_session
app_session.SessionLocal = TestingSessionLocal
app_session.engine = test_engine


@pytest.fixture(autouse=True)
def setup_test_db():
    original_key = settings.GEMINI_API_KEY
    settings.GEMINI_API_KEY = None  # Ensure deterministic fast mock for unit test suite
    Base.metadata.create_all(bind=test_engine)
    yield
    settings.GEMINI_API_KEY = original_key


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def mock_llm():
    return MockLLMProvider()
