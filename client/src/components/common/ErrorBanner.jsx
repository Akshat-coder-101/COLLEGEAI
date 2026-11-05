import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { cn } from '../../utils/cn';
import { Button } from './Button';

export const ErrorBanner = ({
  title = "An error occurred",
  message = "Failed to communicate with research services.",
  onRetry,
  className,
}) => {
  return (
    <div className={cn("p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-900 flex items-start gap-3", className)}>
      <AlertCircle className="w-5 h-5 text-rose-600 mt-0.5 flex-shrink-0" />
      <div className="flex-1">
        <h4 className="text-sm font-semibold text-rose-900">{title}</h4>
        <p className="text-xs text-rose-700 mt-0.5 leading-relaxed">{message}</p>
        {onRetry && (
          <div className="mt-3">
            <Button
              variant="outline"
              size="sm"
              onClick={onRetry}
              className="border-rose-300 text-rose-700 hover:bg-rose-100"
              icon={RefreshCw}
            >
              Retry
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

