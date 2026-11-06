import React from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'motion/react';
import { FolderSearch } from 'lucide-react';
import { Navbar } from '../components/layout/Navbar';
import { WorkspaceHeader } from '../components/workspace/WorkspaceHeader';
import { ResearchProgress } from '../components/workspace/ResearchProgress';
import { WorkspaceTabs } from '../components/workspace/WorkspaceTabs';
import { OverviewTab } from '../components/research/OverviewTab';
import { SourcesTab } from '../components/research/SourcesTab';
import { ComparisonTab } from '../components/research/ComparisonTab';
import { DiscoveriesTab } from '../components/research/DiscoveriesTab';
import { HypothesesTab } from '../components/research/HypothesesTab';
import { ExperimentsTab } from '../components/research/ExperimentsTab';
import { LoadingState } from '../components/common/LoadingState';
import { EmptyState } from '../components/common/EmptyState';
import { ErrorBanner } from '../components/common/ErrorBanner';
import { Card } from '../components/common/Card';
import { useResearchProject } from '../hooks/useResearchProject';

export const ResearchWorkspace = () => {
  const { projectId } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  const currentTab = searchParams.get('tab') || 'overview';
  const { project, isLoading, error, refetch } = useResearchProject(projectId);

  const handleTabChange = (newTabId) => {
    setSearchParams({ tab: newTabId });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col">
        <Navbar />
        <main className="flex-1 flex items-center justify-center p-6">
          <LoadingState
            message="Connecting to HypothesisLab analytical services..."
            subtext="Loading verified citations, comparative consensus, and testable hypotheses."
          />
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col">
        <Navbar />
        <main className="flex-1 max-w-4xl mx-auto w-full px-4 py-16">
          <ErrorBanner
            title="Failed to Load Research Project"
            message={error}
            onRetry={refetch}
          />
        </main>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col">
        <Navbar />
        <main className="flex-1 max-w-4xl mx-auto w-full px-4 py-16">
          <Card className="p-8">
            <EmptyState
              icon={FolderSearch}
              title="Workspace Not Found"
              description={`Unable to locate research project '${projectId}'. It may have been deleted or does not exist.`}
              actionLabel="Return to All Projects"
              onAction={() => navigate('/')}
            />
          </Card>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans selection:bg-scientific-100 selection:text-scientific-900">
      <Navbar />

      {/* Workspace Header */}
      <WorkspaceHeader project={project} onRefresh={refetch} />

      {/* Real-time Multi-Stage Progress */}
      {project.workflow && (
        <ResearchProgress workflow={project.workflow} />
      )}

      {/* Internal Tabs Navigator */}
      <WorkspaceTabs
        activeTab={currentTab}
        onTabChange={handleTabChange}
        stats={project.stats || {}}
        hasExperiments={Boolean(project.experiments)}
      />

      {/* Main Tab Panel with subtle transitions */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentTab}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.16, ease: "easeOut" }}
          >
            {currentTab === 'overview' && (
              <OverviewTab data={project} onSelectTab={handleTabChange} />
            )}
            {currentTab === 'sources' && (
              <SourcesTab sources={project.sources || []} />
            )}
            {currentTab === 'comparisons' && (
              <ComparisonTab comparisons={project.comparisons} />
            )}
            {currentTab === 'discoveries' && (
              <DiscoveriesTab discoveries={project.discoveries} />
            )}
            {currentTab === 'hypotheses' && (
              <HypothesesTab hypotheses={project.hypotheses || []} />
            )}
            {currentTab === 'experiments' && (
              <ExperimentsTab
                experiments={project.experiments}
                projectId={project.id}
                onRefresh={refetch}
              />
            )}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
};
