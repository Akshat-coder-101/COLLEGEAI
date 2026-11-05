import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowUpRight, BookOpen, Sparkles, Clock, FolderGit2, Trash2 } from 'lucide-react';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import { Button } from '../common/Button';
import { EmptyState } from '../common/EmptyState';
import { formatRelativeTime } from '../../utils/formatters';

export const RecentProjects = ({ projects = [], onDeleteProject }) => {
  const getStatusBadge = (status) => {
    switch (status) {
      case 'completed':
        return <Badge variant="success" dot size="sm">Completed</Badge>;
      case 'processing':
        return <Badge variant="warning" dot size="sm">In Progress</Badge>;
      case 'failed':
        return <Badge variant="danger" dot size="sm">Failed</Badge>;
      default:
        return <Badge variant="default" size="sm">{status || 'Initiated'}</Badge>;
    }
  };

  return (
    <div className="max-w-4xl mx-auto mt-10 sm:mt-12 mb-16 px-4">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-base sm:text-lg font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <FolderGit2 className="w-5 h-5 text-scientific-600" />
            <span>Recent Research Workspaces</span>
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Access previous hypothesis formulation workspaces and evidence audits
          </p>
        </div>
        {projects.length > 0 && (
          <span className="text-xs font-mono text-slate-500 bg-slate-100 px-2.5 py-1 rounded-full border border-slate-200">
            {projects.length}
          </span>
        )}
      </div>

      {projects.length === 0 ? (
        <Card className="p-8">
          <EmptyState
            icon={FolderGit2}
            title="No research workspaces yet"
            description="Submit your first scientific inquiry above to formulate hypotheses, analyze evidence, and track discoveries."
          />
        </Card>
      ) : (
        <div className="space-y-3">
          {projects.map((project) => (
            <Card
              key={project.id}
              hoverable
              className="p-4 sm:p-5 group transition-all duration-150 border-slate-200/80 hover:border-scientific-300"
            >
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 sm:gap-4">
                <div className="space-y-2 flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-1.5 sm:gap-2">
                    {getStatusBadge(project.status)}
                    {project.domain && (
                      <Badge variant="primary" size="sm">
                        {project.domain}
                      </Badge>
                    )}
                    <span className="text-[11px] text-slate-400 flex items-center gap-1 font-mono">
                      <Clock className="w-3 h-3" />
                      {formatRelativeTime(project.createdAt)}
                    </span>
                  </div>

                  <Link
                    to={`/research/${project.id}`}
                    className="block group-hover:text-scientific-600 transition-colors"
                  >
                    <h3 className="text-sm sm:text-base font-semibold text-slate-900 leading-snug break-words">
                      {project.title}
                    </h3>
                  </Link>

                  <div className="flex flex-wrap items-center gap-3 sm:gap-4 text-xs text-slate-500 pt-0.5">
                    <span className="flex items-center gap-1.5">
                      <BookOpen className="w-3.5 h-3.5 text-slate-400" />
                      <span className="font-medium text-slate-700">{project.sourceCount || 0}</span> Sources
                    </span>
                    <span className="flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-amber-500" />
                      <span className="font-medium text-slate-700">{project.hypothesisCount || 0}</span> Hypotheses
                    </span>
                    {project.gapCount !== undefined && (
                      <span className="flex items-center gap-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
                        <span className="font-medium text-slate-700">{project.gapCount}</span> Gaps
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex items-center justify-between sm:justify-end gap-2 sm:self-center flex-shrink-0 pt-2 sm:pt-0 border-t sm:border-t-0 border-slate-100">
                  {onDeleteProject && (
                    <button
                      type="button"
                      onClick={(e) => {
                        e.preventDefault();
                        onDeleteProject(project.id);
                      }}
                      className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                      title="Delete project"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                  <Link to={`/research/${project.id}`} className="w-full sm:w-auto">
                    <Button variant="secondary" size="sm" icon={ArrowUpRight} iconPosition="right" className="w-full sm:w-auto">
                      Open Workspace
                    </Button>
                  </Link>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
