import { useState, useEffect, useCallback } from 'react';
import { researchService } from '../services/researchService';

export function useRecentProjects() {
  const [projects, setProjects] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchProjects = useCallback(async () => {
    setIsLoading(true);
    try {
      setError(null);
      const data = await researchService.getProjects();
      setProjects(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Error loading recent projects:", err);
      setError(err.message || 'Failed to retrieve recent research projects.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  const deleteProject = async (projectId) => {
    try {
      await researchService.deleteProject(projectId);
      setProjects((prev) => prev.filter((p) => p.id !== projectId));
    } catch (err) {
      console.error(`Error deleting project ${projectId}:`, err);
    }
  };

  return {
    projects,
    isLoading,
    error,
    refresh: fetchProjects,
    deleteProject,
  };
}

