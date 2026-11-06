import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Navbar } from '../components/layout/Navbar';
import { HeroSection } from '../components/home/HeroSection';
import { ResearchInput } from '../components/home/ResearchInput';
import { RecentProjects } from '../components/home/RecentProjects';
import { ErrorBanner } from '../components/common/ErrorBanner';
import { researchService } from '../services/researchService';
import { useRecentProjects } from '../hooks/useRecentProjects';

export const Home = () => {
  const navigate = useNavigate();
  const { projects, deleteProject, refresh } = useRecentProjects();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submissionError, setSubmissionError] = useState(null);

  const handleStartResearch = async (formData) => {
    setIsSubmitting(true);
    setSubmissionError(null);
    try {
      // 1. Create project via service layer
      const created = await researchService.createProject({
        question: formData.question,
        domain: formData.domain,
        scope: formData.scope,
        enableSimulation: formData.enableSimulation !== undefined ? formData.enableSimulation : true,
        simulationDemands: formData.simulationDemands || null,
      });

      const projectId = created.id;

      // 2. Upload supporting documents if present
      if (formData.files && formData.files.length > 0) {
        await researchService.uploadDocuments(projectId, formData.files);
      }

      // 3. Trigger research workflow
      await researchService.startResearch(projectId);

      // Refresh project list optimistically
      refresh();

      // 4. Navigate directly to the Research Workspace
      navigate(`/research/${projectId}`);
    } catch (error) {
      console.error("Error creating research project:", error);
      setSubmissionError(error.message || 'Failed to initialize research project.');
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans selection:bg-scientific-100 selection:text-scientific-900">
      <Navbar />

      <main className="flex-1 pb-16">
        <HeroSection />

        {submissionError && (
          <div className="max-w-4xl mx-auto px-4 mb-4">
            <ErrorBanner
              title="Failed to start research"
              message={submissionError}
              onRetry={() => setSubmissionError(null)}
            />
          </div>
        )}

        <ResearchInput onSubmit={handleStartResearch} isLoading={isSubmitting} />
        <RecentProjects projects={projects} onDeleteProject={deleteProject} />
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200/80 bg-white py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>HypothesisLab AI — Multi-Agent Research Discovery Platform</span>
          <span className="font-mono text-[11px] text-slate-400">
            {import.meta.env.VITE_USE_MOCK === 'true' ? 'Connected: Local Mock Adapter' : `Connected: FastAPI (${import.meta.env.VITE_API_BASE_URL})`}
          </span>
        </div>
      </footer>
    </div>
  );
};
