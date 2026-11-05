# HypothesisLab AI — Frontend-to-Backend API Contract

This document specifies the exact REST API contract implemented by the React frontend in `client/src/services/researchService.js`.

The backend is developed with **Python FastAPI**.

**Base URL:**
```text
http://localhost:8000/api/v1
```
(Configurable in `client/.env` via `VITE_API_BASE_URL`)

---

## 1. Project Management Endpoints

### 1.1 List Recent Projects
- **Endpoint:** `GET /projects`
- **Response `200 OK`:**
```json
[
  {
    "id": "proj_amyloid_microglia_2026",
    "title": "Role of TREM2-mediated microglial clearance...",
    "domain": "Neuroscience & Cognitive Science",
    "scope": "Comprehensive Synthesis",
    "status": "completed",
    "createdAt": "2026-11-03T14:32:00Z",
    "sourceCount": 14,
    "gapCount": 3,
    "hypothesisCount": 2
  }
]
```

### 1.2 Create Research Project
- **Endpoint:** `POST /projects`
- **Request Body:**
```json
{
  "question": "How does microglial TREM2 signaling modulate tau spreading?",
  "domain": "Neuroscience & Cognitive Science",
  "scope": "Comprehensive Synthesis"
}
```
- **Response `201 Created`:**
```json
{
  "id": "proj_trem2_tau_abc123",
  "title": "How does microglial TREM2 signaling modulate tau spreading?",
  "question": "How does microglial TREM2 signaling modulate tau spreading?",
  "domain": "Neuroscience & Cognitive Science",
  "scope": "Comprehensive Synthesis",
  "status": "processing",
  "createdAt": "2026-11-05T18:00:00Z"
}
```

### 1.3 Upload Supporting PDF Documents
- **Endpoint:** `POST /projects/{projectId}/documents`
- **Content-Type:** `multipart/form-data`
- **Form Key:** `files` (Array of PDF files)
- **Response `200 OK`:**
```json
{
  "projectId": "proj_trem2_tau_abc123",
  "uploadedCount": 2,
  "status": "indexed"
}
```

### 1.4 Start Research Workflow
- **Endpoint:** `POST /projects/{projectId}/start`
- **Response `202 Accepted`:**
```json
{
  "projectId": "proj_trem2_tau_abc123",
  "status": "processing",
  "currentStage": "retrieval"
}
```

---

## 2. Research Results & Detail Endpoints

### 2.1 Get Full Project Details
- **Endpoint:** `GET /projects/{projectId}`
- **Response `200 OK`:** Returns full project model including `overview`, `sources`, `comparisons`, `discoveries`, and `hypotheses`.

### 2.2 Get Workflow Status
- **Endpoint:** `GET /projects/{projectId}/status`
- **Response `200 OK`:**
```json
{
  "projectId": "proj_trem2_tau_abc123",
  "status": "processing",
  "workflow": {
    "currentStage": "extraction",
    "stages": [
      { "id": "retrieval", "name": "Literature Ingestion", "status": "completed", "timestamp": "0s" },
      { "id": "extraction", "name": "Evidence Extraction", "status": "in-progress", "timestamp": "Active" },
      { "id": "comparison", "name": "Comparative Synthesis", "status": "pending" },
      { "id": "discovery", "name": "Gap Detection", "status": "pending" },
      { "id": "hypotheses", "name": "Hypothesis Formulation", "status": "pending" }
    ]
  }
}
```

### 2.3 Get Sources & Evidence
- **Endpoint:** `GET /projects/{projectId}/sources`
- **Response `200 OK`:** Array of paper citations, DOIs, extracted findings, and verbatim supporting quotes with page references.

### 2.4 Get Comparative Analysis
- **Endpoint:** `GET /projects/{projectId}/comparisons`
- **Response `200 OK`:** Object containing `agreements`, `contradictions` (with `conflict`, `contextDifference`, `resolution`), and `comparisonTable`.

### 2.5 Get Research Discoveries
- **Endpoint:** `GET /projects/{projectId}/discoveries`
- **Response `200 OK`:** Object containing `gaps` (with `confidence` and `significance`), `crossDomainConnections`, and `knowledgeGraph` (`nodes` and `edges`).

### 2.6 Get Formulated Hypotheses
- **Endpoint:** `GET /projects/{projectId}/hypotheses`
- **Response `200 OK`:** Array of hypothesis cards containing `statement`, `variables`, `suggestedExperiment`, `supportingEvidence`, `counterarguments`, and `criticalReview`.

### 2.7 Delete Project
- **Endpoint:** `DELETE /projects/{projectId}`
- **Response `200 OK`:**
```json
{
  "success": true
}
```

---

## 3. Switching Between Mock Mode and Real Backend

In `client/.env`:
- To use the local offline mock adapter: `VITE_USE_MOCK=true`
- To connect to the running FastAPI server: `VITE_USE_MOCK=false`

