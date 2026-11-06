import apiClient from './api';
import { mockAdapter } from '../mock/mockAdapter';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

/**
 * =========================================================================
 * HYPOTHESISLAB AI — API INTEGRATION LAYER
 * =========================================================================
 * 
 * This service defines the HTTP contract between the React frontend and 
 * the Python FastAPI backend.
 * 
 * Set VITE_USE_MOCK=false in client/.env to route calls to the live FastAPI server.
 * Default Base URL: http://localhost:8000/api/v1
 * =========================================================================
 */

export const researchService = {
  /**
   * List all historical research projects
   * Backend Endpoint: GET /projects
   */
  async getProjects() {
    if (USE_MOCK) return mockAdapter.getProjects();
    return apiClient.get('/projects');
  },

  /**
   * Retrieve a single project's complete details and results
   * Backend Endpoint: GET /projects/{projectId}
   */
  async getProjectById(projectId) {
    if (USE_MOCK) return mockAdapter.getProjectById(projectId);
    return apiClient.get(`/projects/${projectId}`);
  },

  /**
   * Create a new research project
   * Backend Endpoint: POST /projects
   * Body: { question: string, domain?: string, scope?: string }
   */
  async createProject(payload) {
    if (USE_MOCK) return mockAdapter.createProject(payload);
    return apiClient.post('/projects', {
      question: payload.question,
      domain: payload.domain,
      scope: payload.scope,
      enable_simulation: payload.enableSimulation !== undefined ? payload.enableSimulation : true,
      simulation_demands: payload.simulationDemands || null,
    });
  },

  /**
   * Upload supporting PDF documents for a project
   * Backend Endpoint: POST /projects/{projectId}/documents
   * Content-Type: multipart/form-data
   */
  async uploadDocuments(projectId, files = []) {
    if (USE_MOCK) return mockAdapter.uploadDocuments(projectId, files);
    if (!files || files.length === 0) return { uploadedCount: 0 };

    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });

    return apiClient.post(`/projects/${projectId}/documents`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  /**
   * Trigger the multi-agent research workflow
   * Backend Endpoint: POST /projects/{projectId}/start
   */
  async startResearch(projectId) {
    if (USE_MOCK) return mockAdapter.startResearch(projectId);
    return apiClient.post(`/projects/${projectId}/start`);
  },

  /**
   * Retrieve real-time workflow execution progress
   * Backend Endpoint: GET /projects/{projectId}/status
   */
  async getWorkflowStatus(projectId) {
    if (USE_MOCK) return mockAdapter.getWorkflowStatus(projectId);
    return apiClient.get(`/projects/${projectId}/status`);
  },

  /**
   * Fetch extracted literature sources and supporting citations
   * Backend Endpoint: GET /projects/{projectId}/sources
   */
  async getSources(projectId) {
    if (USE_MOCK) return mockAdapter.getSources(projectId);
    return apiClient.get(`/projects/${projectId}/sources`);
  },

  /**
   * Fetch cross-paper comparative consensus and contradictions
   * Backend Endpoint: GET /projects/{projectId}/comparisons
   */
  async getComparisons(projectId) {
    if (USE_MOCK) return mockAdapter.getComparisons(projectId);
    return apiClient.get(`/projects/${projectId}/comparisons`);
  },

  /**
   * Fetch uncovered research gaps and cross-domain connections
   * Backend Endpoint: GET /projects/{projectId}/discoveries
   */
  async getDiscoveries(projectId) {
    if (USE_MOCK) return mockAdapter.getDiscoveries(projectId);
    return apiClient.get(`/projects/${projectId}/discoveries`);
  },

  /**
   * Fetch formulated testable hypotheses and critical reviews
   * Backend Endpoint: GET /projects/{projectId}/hypotheses
   */
  async getHypotheses(projectId) {
    if (USE_MOCK) return mockAdapter.getHypotheses(projectId);
    return apiClient.get(`/projects/${projectId}/hypotheses`);
  },

  /**
   * Run in silico computational simulation for a project
   * Backend Endpoint: POST /projects/{projectId}/simulate
   */
  async runSimulation(projectId) {
    if (USE_MOCK) return mockAdapter.runSimulation ? mockAdapter.runSimulation(projectId) : {};
    return apiClient.post(`/projects/${projectId}/simulate`);
  },

  /**
   * Delete a research project
   * Backend Endpoint: DELETE /projects/{projectId}
   */
  async deleteProject(projectId) {
    if (USE_MOCK) return mockAdapter.deleteProject(projectId);
    return apiClient.delete(`/projects/${projectId}`);
  },
};

export default researchService;

