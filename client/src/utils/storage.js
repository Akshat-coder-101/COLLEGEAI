import { DEFAULT_RECENT_PROJECTS } from './constants';

const STORAGE_KEY = 'hypothesislab_projects';

export function getStoredProjects() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(DEFAULT_RECENT_PROJECTS));
      return DEFAULT_RECENT_PROJECTS;
    }
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : DEFAULT_RECENT_PROJECTS;
  } catch (e) {
    console.error("Failed to read projects from storage", e);
    return DEFAULT_RECENT_PROJECTS;
  }
}

export function saveProject(project) {
  try {
    const current = getStoredProjects();
    const existingIndex = current.findIndex(p => p.id === project.id);
    let updated;
    if (existingIndex >= 0) {
      updated = [...current];
      updated[existingIndex] = { ...updated[existingIndex], ...project };
    } else {
      updated = [project, ...current];
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
    return updated;
  } catch (e) {
    console.error("Failed to save project to storage", e);
    return getStoredProjects();
  }
}

export function getProjectById(id) {
  const projects = getStoredProjects();
  return projects.find(p => p.id === id) || null;
}

