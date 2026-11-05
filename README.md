# HypothesisLab AI

HypothesisLab AI is a multi-agent scientific hypothesis formulation and research discovery platform.

## Repository Overview

- **`/client`**: The React + Vite frontend application (Tailwind CSS, Watermelon UI architecture, DaisyUI, Motion, Recharts, React Flow).
- **`/client/API_CONTRACT.md`**: Complete REST API contract, request schemas, multipart PDF upload specifications, and JSON response models for the FastAPI backend.
- **Backend**: Under independent development using Python FastAPI.

---

## Backend Teammate Quick Start

For the backend engineer developing the FastAPI services:
1. **API Contract:** Read [`client/API_CONTRACT.md`](./client/API_CONTRACT.md) for all expected endpoints, payloads, and response structures.
2. **Default API Base URL:** `http://localhost:8000/api/v1`
3. **Core Endpoints Needed:**
   - `GET /api/v1/projects` (List research projects)
   - `POST /api/v1/projects` (Create a research project)
   - `GET /api/v1/projects/{projectId}` (Get full project details & results)
   - `POST /api/v1/projects/{projectId}/documents` (Upload PDFs, multipart/form-data)
   - `POST /api/v1/projects/{projectId}/start` (Start multi-agent research workflow)
   - `GET /api/v1/projects/{projectId}/status` (Retrieve workflow progress)
   - `GET /api/v1/projects/{projectId}/sources` (Extracted papers, citations & quotes)
   - `GET /api/v1/projects/{projectId}/comparisons` (Cross-paper agreements & contradictions)
   - `GET /api/v1/projects/{projectId}/discoveries` (Gaps, cross-domain links & graph)
   - `GET /api/v1/projects/{projectId}/hypotheses` (Formulated testable hypotheses & critical reviews)

---

## Running the Frontend Client

```bash
cd client
npm install
npm run dev
```

Runs at `http://localhost:5173`.
- Set `VITE_USE_MOCK=false` in `client/.env` to connect directly to your local FastAPI backend.
- Set `VITE_USE_MOCK=true` to test in offline mock mode.
