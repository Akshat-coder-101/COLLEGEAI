import { MOCK_PROJECT_DETAILS } from './mockData';
import { getStoredProjects, saveProject, getProjectById } from '../utils/storage';

/**
 * Mock Adapter for HypothesisLab AI
 * Used during UI development and offline previews.
 * Isolated completely from real API services and easily toggled off.
 */

const delay = (ms = 250) => new Promise((resolve) => setTimeout(resolve, ms));

export const mockAdapter = {
  async getProjects() {
    await delay(200);
    return getStoredProjects();
  },

  async getProjectById(projectId) {
    await delay(300);
    const stored = getProjectById(projectId);
    if (!stored) {
      if (projectId === MOCK_PROJECT_DETAILS.id) {
        return MOCK_PROJECT_DETAILS;
      }
      return null;
    }

    // Merge stored metadata with full mock analysis dataset for rich preview
    return {
      ...MOCK_PROJECT_DETAILS,
      id: stored.id,
      title: stored.title || MOCK_PROJECT_DETAILS.title,
      question: stored.title || MOCK_PROJECT_DETAILS.question,
      domain: stored.domain || MOCK_PROJECT_DETAILS.domain,
      scope: stored.scope || MOCK_PROJECT_DETAILS.scope,
      createdAt: stored.createdAt || MOCK_PROJECT_DETAILS.createdAt,
      status: stored.status || 'completed',
    };
  },

  async createProject(payload) {
    await delay(350);
    const cleanSlug = payload.question
      .toLowerCase()
      .replace(/[^a-z0-9]/g, '_')
      .replace(/_+/g, '_')
      .slice(0, 32);
    const projectId = `proj_${cleanSlug}_${Date.now().toString(36)}`;

    const newProject = {
      id: projectId,
      title: payload.question,
      question: payload.question,
      domain: payload.domain || 'Cross-Disciplinary',
      scope: payload.scope || 'Comprehensive Synthesis',
      status: 'processing',
      createdAt: new Date().toISOString(),
      sourceCount: payload.files ? payload.files.length : 0,
      gapCount: 0,
      hypothesisCount: 0,
      files: payload.files ? payload.files.map((f) => ({ name: f.name, size: f.size })) : [],
      workflow: {
        currentStage: 'extraction',
        startedAt: new Date().toLocaleTimeString(),
        stages: [
          { id: 'retrieval', name: 'Literature Ingestion', status: 'completed', timestamp: '0s' },
          { id: 'extraction', name: 'Evidence Extraction', status: 'in-progress', timestamp: 'Active' },
          { id: 'comparison', name: 'Comparative Synthesis', status: 'pending' },
          { id: 'discovery', name: 'Gap Detection', status: 'pending' },
          { id: 'hypotheses', name: 'Hypothesis Formulation', status: 'pending' },
        ],
      },
    };

    saveProject(newProject);
    return newProject;
  },

  async uploadDocuments(projectId, files) {
    await delay(400);
    return {
      projectId,
      uploadedCount: files.length,
      status: 'indexed',
    };
  },

  async startResearch(projectId) {
    await delay(200);
    return {
      projectId,
      status: 'processing',
      currentStage: 'retrieval',
    };
  },

  async getWorkflowStatus(projectId) {
    await delay(150);
    const project = await this.getProjectById(projectId);
    return {
      projectId,
      status: project?.status || 'completed',
      workflow: project?.workflow || null,
    };
  },

  async getSources(projectId) {
    await delay(200);
    const project = await this.getProjectById(projectId);
    return project?.sources || [];
  },

  async getComparisons(projectId) {
    await delay(200);
    const project = await this.getProjectById(projectId);
    return project?.comparisons || null;
  },

  async getDiscoveries(projectId) {
    await delay(200);
    const project = await this.getProjectById(projectId);
    return project?.discoveries || null;
  },

  async getHypotheses(projectId) {
    await delay(200);
    const project = await this.getProjectById(projectId);
    return project?.hypotheses || [];
  },

  async deleteProject(projectId) {
    await delay(150);
    const current = getStoredProjects();
    const filtered = current.filter((p) => p.id !== projectId);
    localStorage.setItem('hypothesislab_projects', JSON.stringify(filtered));
    return { success: true };
  },
};

