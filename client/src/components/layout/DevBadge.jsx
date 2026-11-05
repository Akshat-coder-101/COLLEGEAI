import React from 'react';
import { FlaskConical } from 'lucide-react';

export const DevBadge = () => {
  const isMock = import.meta.env.VITE_USE_MOCK === 'true';

  if (!isMock) return null;

  return (
    <div 
      title="Running in Local Mock Adapter Mode. Real backend calls can be toggled via VITE_USE_MOCK=false in .env"
      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-mono font-medium bg-amber-50 text-amber-800 border border-amber-200 shadow-xs"
    >
      <FlaskConical className="w-3.5 h-3.5 text-amber-600 animate-pulse" />
      <span className="hidden sm:inline">DEV MOCK ADAPTER</span>
      <span className="sm:hidden">MOCK</span>
    </div>
  );
};

