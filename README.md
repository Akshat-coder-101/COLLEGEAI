# HypothesisLab AI

HypothesisLab AI is an autonomous multi-agent scientific hypothesis formulation, research discovery, and computational experimentation platform.

---

## Repository Architecture

```text
COLLEGEAI/
├── client/                     # React + Vite frontend application
│   ├── src/
│   │   ├── components/         # Modular Watermelon UI components (Research workspace, tabs, graphs)
│   │   ├── services/           # Axios API client & researchService HTTP layer
│   │   ├── mock/               # Offline preview mock adapter & datasets
│   │   └── pages/              # Home & ResearchWorkspace views
│   ├── .env.example
│   ├── API_CONTRACT.md         # Full REST API specification implemented by React client
│   └── package.json
├── server/                     # Python FastAPI multi-agent research backend
│   ├── app/
│   │   ├── main.py             # FastAPI entrypoint & CORS middleware
│   │   ├── config.py           # Pydantic settings & environment configuration
│   │   ├── api/routes/         # /projects, /research, /documents, /discoveries, /experiments
│   │   ├── agents/             # Multi-agent autonomous research & simulation pipeline
│   │   │   ├── research_planner.py
│   │   │   ├── literature_discovery.py
│   │   │   ├── research_analysis.py
│   │   │   ├── cross_domain_discovery.py
│   │   │   ├── gap_detection.py
│   │   │   ├── hypothesis_generation.py
│   │   │   ├── critical_reviewer.py
│   │   │   └── simulation/     # Repo discovery, validation, model builder, benchmark testing
│   │   ├── workflows/          # Asynchronous research & simulation pipelines
│   │   ├── services/           # LLM, document extraction (PyMuPDF), KnowledgeGraph (NetworkX)
│   │   ├── simulation/         # Isolated sandbox execution & independent benchmarks
│   │   └── models/             # SQLAlchemy ORM models (SQLite & PostgreSQL)
│   ├── tests/                  # Complete Pytest test suite (28 passing tests)
│   ├── requirements.txt
│   └── .env.example
├── .gitignore
└── README.md
```

---

## Local Setup & Execution

### 1. Start the Backend (FastAPI)

```bash
cd server
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API Base URL: `http://localhost:8000/api/v1`
- Interactive Swagger Documentation: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/v1/health`

To run backend tests:
```bash
pytest server/tests -v
```

### 2. Start the Frontend Client (React + Vite)

```bash
cd client
npm install
npm run dev
```

- Web UI runs at `http://localhost:5173`
- Connected to live backend via `VITE_API_BASE_URL=http://localhost:8000/api/v1` in `client/.env`
- Toggle `VITE_USE_MOCK=true` or `false` in `client/.env` to switch between live backend and offline mock mode.

---

## Integrated API Endpoints

- `GET /api/v1/projects`: List historical and active projects
- `POST /api/v1/projects`: Create a new research project
- `POST /api/v1/projects/{id}/documents`: Multipart PDF upload with SHA-256 duplicate detection
- `POST /api/v1/projects/{id}/start`: Launch asynchronous autonomous multi-agent research workflow
- `GET /api/v1/projects/{id}/status`: Real-time stage polling (`retrieval`, `extraction`, `comparison`, `discovery`, `hypotheses`, `completed`)
- `GET /api/v1/projects/{id}`: Complete project overview, sources, comparisons, discoveries, hypotheses, and knowledge graph
- `GET /api/v1/projects/{id}/sources`: Verified citations and supporting quotes with page references
- `GET /api/v1/projects/{id}/comparisons`: Cross-paper agreements and contradictions
- `GET /api/v1/projects/{id}/discoveries`: Gaps, cross-domain connections, and NetworkX knowledge graph
- `GET /api/v1/projects/{id}/hypotheses`: Formulated testable hypotheses with operational variables, protocols, and critical reviews
- `DELETE /api/v1/projects/{id}`: Delete research project
