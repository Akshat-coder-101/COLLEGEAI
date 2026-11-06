import React from 'react';
import { LayoutDashboard, BookOpen, Scale, Sparkles, FlaskConical, Workflow } from 'lucide-react';
import { cn } from '../../utils/cn';

export const WorkspaceTabs = ({ activeTab, onTabChange, stats = {}, hasExperiments = false }) => {
  const tabs = [
    {
      id: 'overview',
      label: 'Overview',
      icon: LayoutDashboard,
      badge: null,
    },
    {
      id: 'sources',
      label: 'Sources & Evidence',
      icon: BookOpen,
      badge: stats.papersReviewed !== undefined ? stats.papersReviewed : null,
    },
    {
      id: 'comparisons',
      label: 'Comparative Analysis',
      icon: Scale,
      badge: null,
    },
    {
      id: 'discoveries',
      label: 'Research Discoveries',
      icon: Sparkles,
      badge: stats.gapsIdentified !== undefined ? stats.gapsIdentified : null,
    },
    {
      id: 'hypotheses',
      label: 'Hypotheses',
      icon: FlaskConical,
      badge: stats.hypothesesFormulated !== undefined ? stats.hypothesesFormulated : null,
    },
    {
      id: 'experiments',
      label: 'Computational Validation',
      icon: Workflow,
      badge: hasExperiments ? 'Verified' : 'In Silico',
    },
  ];

  return (
    <div className="bg-white border-b border-slate-200 sticky top-16 z-30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <nav className="flex space-x-1 sm:space-x-4 overflow-x-auto py-2 no-scrollbar" aria-label="Tabs">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;

            return (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={cn(
                  "flex items-center gap-2 py-2 px-3 rounded-lg text-xs sm:text-sm font-medium whitespace-nowrap transition-all duration-150 relative",
                  isActive
                    ? "bg-scientific-50 text-scientific-700 font-semibold"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-100/70"
                )}
              >
                <Icon className={cn("w-4 h-4", isActive ? "text-scientific-600" : "text-slate-400")} />
                <span>{tab.label}</span>
                {tab.badge !== null && tab.badge !== undefined && (
                  <span
                    className={cn(
                      "text-[10px] font-mono px-1.5 py-0.2 rounded-full",
                      isActive
                        ? "bg-scientific-200/80 text-scientific-800 font-semibold"
                        : "bg-slate-100 text-slate-500"
                    )}
                  >
                    {tab.badge}
                  </span>
                )}
                {isActive && (
                  <span className="absolute bottom-[-9px] left-2 right-2 h-0.5 bg-scientific-600 rounded-full" />
                )}
              </button>
            );
          })}
        </nav>
      </div>
    </div>
  );
};

