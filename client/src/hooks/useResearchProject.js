import { useState, useEffect, useCallback, useRef } from 'react';
import { researchService } from '../services/researchService';

export function useResearchProject(projectId, { autoPoll = true, pollIntervalMs = 4000 } = {}) {
  const [project, setProject] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const pollTimerRef = useRef(null);

  const fetchProject = useCallback(async () => {
    if (!projectId) return;
    try {
      setError(null);
      const data = await researchService.getProjectById(projectId);
      setProject(data);
      return data;
    } catch (err) {
      console.error(`Error fetching project ${projectId}:`, err);
      setError(err.message || 'Failed to load project details.');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  // Initial load
  useEffect(() => {
    fetchProject();
  }, [fetchProject]);

  // Status polling for active processing workflows
  useEffect(() => {
    if (!autoPoll || !project) return;

    if (project.status === 'processing' || project.status === 'in-progress') {
      pollTimerRef.current = setInterval(async () => {
        try {
          const statusRes = await researchService.getWorkflowStatus(projectId);
          if (statusRes.status !== 'processing' && statusRes.status !== 'in-progress') {
            // Workflow finished or changed; reload full data
            clearInterval(pollTimerRef.current);
            fetchProject();
          } else if (statusRes.workflow) {
            setProject((prev) => (prev ? { ...prev, workflow: statusRes.workflow } : prev));
          }
        } catch (pollErr) {
          console.warn("Polling error (non-fatal):", pollErr);
        }
      }, pollIntervalMs);
    } else {
      if (pollTimerRef.current) clearInterval(pollTimerRef.current);
    }

    return () => {
      if (pollTimerRef.current) clearInterval(pollTimerRef.current);
    };
  }, [autoPoll, project?.status, projectId, fetchProject, pollIntervalMs]);

  return {
    project,
    isLoading,
    error,
    refetch: fetchProject,
  };
}

