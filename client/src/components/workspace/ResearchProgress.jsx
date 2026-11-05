import React from 'react';
import { CheckCircle2, Loader2, Circle, Clock } from 'lucide-react';
import { cn } from '../../utils/cn';

export const ResearchProgress = ({ workflow, isCompact = false }) => {
  if (!workflow || !workflow.stages || workflow.stages.length === 0) return null;

  const { stages, currentStage } = workflow;

  return (
    <div className={cn("bg-white border-b border-slate-200/80 px-4 sm:px-6 lg:px-8 py-3", isCompact ? "py-2" : "py-3.5")}>
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider font-mono">
              Research Pipeline Status:
            </span>
            <span className="text-xs font-semibold text-slate-800 capitalize">
              {currentStage === 'completed' ? 'All Analytical Stages Finished' : `Executing ${currentStage}...`}
            </span>
          </div>
          {workflow.startedAt && (
            <span className="text-[10px] text-slate-400 font-mono hidden sm:inline">
              Started: {workflow.startedAt}
            </span>
          )}
        </div>

        {/* Pipeline Stage Steps */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2 pt-1">
          {stages.map((stage, idx) => {
            const isCompleted = stage.status === 'completed';
            const isRunning = stage.status === 'in-progress' || stage.status === 'processing';
            const isPending = !isCompleted && !isRunning;

            return (
              <div
                key={stage.id || idx}
                className={cn(
                  "flex items-center gap-2 px-2.5 py-1.5 rounded-lg border text-xs transition-colors",
                  isCompleted && "bg-emerald-50/60 border-emerald-200/80 text-emerald-900",
                  isRunning && "bg-scientific-50 border-scientific-300 text-scientific-900 ring-1 ring-scientific-200",
                  isPending && "bg-slate-50 border-slate-200/70 text-slate-400 opacity-60"
                )}
              >
                <div className="flex-shrink-0">
                  {isCompleted && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />}
                  {isRunning && <Loader2 className="w-3.5 h-3.5 text-scientific-600 animate-spin" />}
                  {isPending && <Circle className="w-3.5 h-3.5 text-slate-300" />}
                </div>

                <div className="truncate flex-1">
                  <div className="font-medium text-[11px] truncate leading-tight">
                    {stage.name}
                  </div>
                  {stage.timestamp && (
                    <div className="text-[9px] font-mono text-slate-400 leading-none">
                      {stage.timestamp}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

