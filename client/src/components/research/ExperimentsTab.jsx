import React from 'react';
import { Workflow, Play, Terminal, AlertCircle } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import { Badge } from '../common/Badge';
import { Button } from '../common/Button';
import { EmptyState } from '../common/EmptyState';

export const ExperimentsTab = ({ experiments }) => {
  if (!experiments) {
    return (
      <Card className="p-8 border-slate-200">
        <EmptyState
          icon={Workflow}
          title="Backend Experiment Execution Not Connected"
          description="In silico experiment simulation, model container execution, and computational validation modules will become available once the backend FastAPI experiment runner service is active."
        />
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card className="p-5 border-slate-200">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Terminal className="w-4 h-4 text-scientific-600" />
            <CardTitle className="text-sm font-semibold">Computational Experiment Runner</CardTitle>
          </div>
          <Badge variant="primary" size="sm">Active Container</Badge>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-xs text-slate-700">
            <span className="font-semibold">Target Repository/Model: </span>
            {experiments.model || "Local Python Runner"}
          </div>
          <div className="text-xs text-slate-700">
            <span className="font-semibold">Execution Status: </span>
            {experiments.status || "Idle"}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

