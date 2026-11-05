# HypothesisLab AI — Backend

Autonomous multi-agent research and discovery platform backend built with FastAPI, LangGraph-style workflow orchestration, SQLAlchemy, NetworkX, and Gemini AI.

HypothesisLab AI coordinates autonomous agents to investigate complex scientific and technical questions:
- Ingests uploaded research papers (PDFs) and queries external academic literature (arXiv, Semantic Scholar).
- Extracts verifiable, evidence-backed scientific findings tied strictly to document locations and exact quotes.
- Identifies cross-domain relationships, explicitly labeling connections as either `explicitly_supported` or `ai_inferred`.
- Detects research gaps, contradictions, and methodological boundaries.
- Synthesizes testable, falsifiable research hypotheses across 10 required PRD dimensions.
- Subjects hypotheses to an independent Critical Reviewer Agent.
- Maintains a reconstructed, directed NetworkX Knowledge Graph with provenance tracking.
- Provides optional computational simulation via GitHub Repository validation (Path A) or grounded NumPy/SciPy model construction (Path B) in an isolated sandbox with independent benchmark verification.

---

## Architecture

```
server/
├── app/
│   ├── main.py                  # FastAPI application setup, routes, lifespan
│   ├── config.py                # Environment configuration via Pydantic Settings
│   ├── api/
│   │   ├── dependencies.py      # Database session injection
│   │   └── routes/
│   │       ├── health.py        # System health & API service configuration
│   │       ├── research.py      # Research project CRUD & workflow execution
│   │       ├── documents.py     # PDF upload, duplicate detection & parsing
│   │       ├── discoveries.py   # Research gaps, relationships & hypotheses
│   │       └── experiments.py   # Simulation workflows, status & validation reports
│   ├── agents/
│   │   ├── research_planner.py       # Domain identification & investigation plans
│   │   ├── literature_discovery.py   # Federated academic search & paper deduplication
│   │   ├── research_analysis.py      # Evidence extraction, parameters & units
│   │   ├── cross_domain_discovery.py # Interdisciplinary relationship labeling
│   │   ├── gap_detection.py          # Contradiction & research boundary detection
│   │   ├── hypothesis_generation.py  # 10-point testable hypothesis synthesis
│   │   ├── critical_reviewer.py      # Independent review & testability evaluation
│   │   └── simulation/
│   │       ├── repository_discovery.py   # GitHub repository search & ranking
│   │       ├── repository_validation.py  # Repository compatibility & safety checks
│   │       ├── model_builder.py          # Grounded numerical model generation
│   │       ├── evidence_validation.py    # Multi-level validation reporting
│   │       ├── simulation_testing.py     # Sandbox execution & benchmark tests
│   │       └── correction.py             # Controlled retry loop & benchmark protection
│   ├── workflows/
│   │   ├── research_workflow.py      # 8-stage asynchronous research pipeline
│   │   └── simulation_workflow.py    # Sandbox simulation & correction pipeline
│   ├── services/
│   │   ├── llm_service.py            # Gemini provider & deterministic test mock
│   │   ├── document_service.py       # PyMuPDF/pypdf extraction & SHA-256 deduplication
│   │   ├── literature_service.py     # arXiv & Semantic Scholar integrations
│   │   ├── evidence_service.py       # Quote span verification & source linkage
│   │   ├── knowledge_graph.py        # NetworkX directed graph & provenance tracing
│   │   └── github_service.py         # GitHub API client & repository inspection
│   ├── simulation/
│   │   ├── sandbox_service.py        # Process isolation, timeouts & prohibited token checks
│   │   ├── benchmark_service.py      # Immutable analytical reference baselines
│   │   └── execution_service.py      # Runner & metrics extractor
│   ├── models/
│   │   └── entities.py               # SQLAlchemy ORM models (SQLite/PostgreSQL)
│   ├── schemas/                      # Pydantic v2 schemas
│   └── database/
│       └── session.py                # Database connection & SessionLocal
├── tests/                            # Comprehensive Pytest test suite (27 tests)
├── uploads/                          # Managed PDF storage
├── requirements.txt
├── .env.example
└── README.md
```

---

## Installation & Setup

### 1. Requirements
- Python 3.11+
- Virtual environment (recommended)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env` and configure your credentials:
```bash
cp .env.example .env
```

Key environment variables:
- `GEMINI_API_KEY`: API key for Gemini models (optional for deterministic test mock).
- `GEMINI_MODEL`: Defaults to `gemini-2.5-flash`.
- `DATABASE_URL`: `sqlite:///./hypothesis_lab.db` (or PostgreSQL `postgresql+psycopg2://...`).
- `SEMANTIC_SCHOLAR_API_KEY`: Optional key for academic paper indexing.
- `GITHUB_TOKEN`: Optional token for GitHub repository discovery.
- `UPLOAD_DIRECTORY`: Directory for uploaded PDF research papers.
- `MAX_SIMULATION_ITERATIONS`: Maximum controlled retry loops (default: 3).
- `SIMULATION_TIMEOUT`: Subprocess timeout in seconds (default: 60).

---

## Running the Backend

Start the development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Base API URL: `http://localhost:8000/api/v1`

---

## API Endpoints

### Health
- `GET /health` or `GET /api/v1/health`

### Research Projects
- `POST /api/v1/research`: Create research project (`title`, `question`, `domain`).
- `GET /api/v1/research`: List all projects.
- `GET /api/v1/research/{project_id}`: Retrieve project metadata.
- `DELETE /api/v1/research/{project_id}`: Delete project and associated records.
- `POST /api/v1/research/{project_id}/run`: Start asynchronous multi-agent research workflow.
- `GET /api/v1/research/{project_id}/status`: Poll workflow stage, progress, and messages.
- `GET /api/v1/research/{project_id}/results`: Retrieve completed findings, gaps, relationships, and hypotheses.

### Document Management
- `POST /api/v1/research/{project_id}/documents`: Upload PDFs (detects duplicates by SHA-256 hash).
- `GET /api/v1/research/{project_id}/documents`: List uploaded documents.
- `DELETE /api/v1/documents/{document_id}`: Remove document.

### Discoveries & Hypotheses
- `GET /api/v1/research/{project_id}/discoveries`: Retrieve gaps, contradictions, and relationships.
- `GET /api/v1/research/{project_id}/hypotheses`: List generated hypotheses.
- `GET /api/v1/hypotheses/{hypothesis_id}`: Retrieve detailed 10-point hypothesis with review scores.

### Simulation
- `POST /api/v1/hypotheses/{hypothesis_id}/simulate`: Initiate Path A or Path B simulation.
- `GET /api/v1/experiments/{experiment_id}`: Retrieve experiment state.
- `GET /api/v1/experiments/{experiment_id}/status`: Poll iteration and execution status.
- `POST /api/v1/experiments/{experiment_id}/retry`: Request controlled correction/retry.
- `GET /api/v1/experiments/{experiment_id}/report`: Retrieve 3-level validation report (`code_tests`, `model_verification`, `empirical_validation`).

---

## Running Tests

Run the complete test suite:
```bash
pytest server/tests -v
```
All 27 integration and unit tests cover:
1. API endpoints & validation schemas
2. PDF text extraction & duplicate document detection
3. Evidence span verification & citation traceability
4. Knowledge graph construction & provenance backtracking
5. Agent outputs & 10-point hypothesis specifications
6. Sandbox security isolation & prohibited token detection
7. GitHub repository discovery & safety inspection
8. Independent benchmark verification & correction loop integrity
9. End-to-end multi-agent research and simulation execution
