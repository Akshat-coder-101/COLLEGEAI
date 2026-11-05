import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Clock, Layers, BookOpen, Download, RefreshCw } from 'lucide-react';
import { Badge } from '../common/Badge';
import { Button } from '../common/Button';
import { formatDate } from '../../utils/formatters';

export const WorkspaceHeader = ({ project, onRefresh }) => {
  if (!project) return null;

  const getStatusBadge = (status) => {
    switch (status) {
      case 'completed':
        return <Badge variant="success" dot size="md">Analysis Completed</Badge>;
      case 'processing':
        return <Badge variant="warning" dot size="md">Workflow In Progress</Badge>;
      case 'failed':
        return <Badge variant="danger" dot size="md">Analysis Failed</Badge>;
      default:
        return <Badge variant="default" size="md">{status || 'Initiated'}</Badge>;
    }
  };

  return (
    <div className="bg-white border-b border-slate-200/90 py-4 sm:py-5 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Navigation & metadata breadcrumb */}
        <div className="flex flex-wrap items-center justify-between gap-2.5 mb-2.5">
          <div className="flex items-center gap-1.5 text-xs text-slate-500">
            <Link to="/" className="inline-flex items-center gap-1 hover:text-scientific-600 font-medium transition-colors">
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>All Workspaces</span>
            </Link>
            <span>/</span>
            <span className="font-mono text-slate-400 truncate max-w-[140px] sm:max-w-[200px]">{project.id}</span>
          </div>

          <div className="flex items-center gap-2">
            {getStatusBadge(project.status)}
            {project.createdAt && (
              <span className="text-[11px] text-slate-400 font-mono hidden sm:flex items-center gap-1 border-l border-slate-200 pl-2">
                <Clock className="w-3 h-3" />
                {formatDate(project.createdAt)}
              </span>
            )}
          </div>
        </div>

        {/* Title and Question */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div className="space-y-1.5 max-w-4xl">
            <h1 className="text-lg sm:text-xl lg:text-2xl font-bold text-slate-900 tracking-tight leading-snug break-words">
              {project.title || project.question}
            </h1>
            {project.question && project.question !== project.title && (
              <p className="text-xs sm:text-sm text-slate-600 italic break-words">
                Inquiry: "{project.question}"
              </p>
            )}

            <div className="flex flex-wrap items-center gap-1.5 pt-0.5">
              {project.domain && (
                <Badge variant="primary" size="sm">
                  <Layers className="w-3 h-3 mr-1" />
                  {project.domain}
                </Badge>
              )}
              {project.scope && (
                <Badge variant="default" size="sm">
                  <BookOpen className="w-3 h-3 mr-1" />
                  {project.scope}
                </Badge>
              )}
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex items-center gap-2 flex-shrink-0 pt-1 lg:pt-0">
            {onRefresh && (
              <Button
                variant="secondary"
                size="sm"
                icon={RefreshCw}
                onClick={onRefresh}
                title="Refresh project state"
              >
                Refresh
              </Button>
            )}
            <Button
              variant="outline"
              size="sm"
              icon={Download}
              onClick={() => {
                const blob = new Blob([JSON.stringify(project, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${project.id}_report.json`;
                a.click();
              }}
            >
              Export JSON
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
