import React from 'react';
import { Loader2 } from 'lucide-react';
import { cn } from '../../utils/cn';

export const LoadingState = ({
  message = "Loading research data...",
  className,
  subtext,
}) => {
  return (
    <div className={cn("flex flex-col items-center justify-center py-16 px-4 text-center", className)}>
      <div className="relative flex items-center justify-center mb-4">
        <div className="w-12 h-12 rounded-full border-2 border-scientific-100 animate-ping opacity-25" />
        <Loader2 className="w-8 h-8 text-scientific-600 animate-spin absolute" />
      </div>
      <p className="text-sm font-medium text-slate-700">{message}</p>
      {subtext && <p className="text-xs text-slate-400 mt-1 max-w-sm">{subtext}</p>}
    </div>
  );
};

export const Skeleton = ({ className }) => (
  <div className={cn("animate-pulse bg-slate-200/80 rounded", className)} />
);

