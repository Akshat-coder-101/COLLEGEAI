import React from 'react';
import { Search } from 'lucide-react';
import { cn } from '../../utils/cn';
import { Button } from './Button';

export const EmptyState = ({
  icon: Icon = Search,
  title = "No data found",
  description = "No items or research results are currently available.",
  actionLabel,
  onAction,
  className,
}) => {
  return (
    <div className={cn("flex flex-col items-center justify-center py-12 px-4 text-center max-w-md mx-auto", className)}>
      <div className="w-12 h-12 rounded-xl bg-slate-100 flex items-center justify-center text-slate-500 mb-4 border border-slate-200">
        <Icon className="w-6 h-6" />
      </div>
      <h3 className="text-base font-semibold text-slate-800 mb-1">{title}</h3>
      <p className="text-xs text-slate-500 mb-6 leading-relaxed">{description}</p>
      {actionLabel && onAction && (
        <Button variant="secondary" size="sm" onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </div>
  );
};

