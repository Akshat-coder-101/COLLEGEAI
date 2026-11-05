import React from 'react';
import { BookOpen, Sparkles, Scale, AlertCircle, ArrowRight, Lightbulb, CheckCircle2, ShieldAlert } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import { Badge } from '../common/Badge';
import { Button } from '../common/Button';

export const OverviewTab = ({ data, onSelectTab }) => {
  if (!data) return null;

  const { overview = {}, stats = {}, question, domain } = data;

  return (
    <div className="space-y-6">
      {/* Metrics Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="p-4 border-slate-200">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Literature Reviewed</span>
            <BookOpen className="w-4 h-4 text-scientific-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900 font-mono">
            {stats.papersReviewed || 0}
          </div>
          <p className="text-[11px] text-slate-400 mt-1">Peer-reviewed publications & preprints</p>
        </Card>

        <Card className="p-4 border-slate-200">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Extracted Findings</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900 font-mono">
            {stats.extractedFindings || 0}
          </div>
          <p className="text-[11px] text-slate-400 mt-1">Verified claims with quote citations</p>
        </Card>

        <Card className="p-4 border-slate-200">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Research Gaps</span>
            <AlertCircle className="w-4 h-4 text-amber-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900 font-mono">
            {stats.gapsIdentified || 0}
          </div>
          <p className="text-[11px] text-slate-400 mt-1">Unexplored mechanisms & blind spots</p>
        </Card>

        <Card className="p-4 border-slate-200">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Formulated Hypotheses</span>
            <Sparkles className="w-4 h-4 text-indigo-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900 font-mono">
            {stats.hypothesesFormulated || 0}
          </div>
          <p className="text-[11px] text-slate-400 mt-1">Testable, falsifiable experimental models</p>
        </Card>
      </div>

      {/* Synthesis Summary */}
      <Card className="border-scientific-200/80 bg-gradient-to-r from-scientific-50/40 via-white to-white">
        <CardHeader className="border-b border-scientific-100">
          <div className="flex items-center gap-2">
            <Lightbulb className="w-4 h-4 text-scientific-600" />
            <CardTitle className="text-base text-slate-900">Executive Literature Synthesis</CardTitle>
          </div>
          {domain && <Badge variant="primary" size="sm">{domain}</Badge>}
        </CardHeader>
        <CardContent className="pt-4 pb-5">
          <p className="text-sm text-slate-700 leading-relaxed">
            {overview.summary || "Literature extraction completed across indexed corpora. Review key findings and identified contradictions below."}
          </p>
        </CardContent>
      </Card>

      {/* Key Findings and Research Gaps Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Key Findings */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between w-full">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <CardTitle className="text-sm font-semibold">Key Extracted Findings</CardTitle>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onSelectTab('sources')}
                className="text-xs text-scientific-600 hover:text-scientific-700"
              >
                View Sources <ArrowRight className="w-3.5 h-3.5 ml-1" />
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {overview.keyFindings && overview.keyFindings.length > 0 ? (
              overview.keyFindings.map((finding, idx) => (
                <div key={idx} className="flex items-start gap-2.5 p-3 rounded-lg bg-slate-50 border border-slate-100 text-xs text-slate-800">
                  <span className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-800 font-mono text-[10px] font-bold flex items-center justify-center flex-shrink-0 mt-0.5">
                    {idx + 1}
                  </span>
                  <p className="leading-relaxed">{finding}</p>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-400">No findings extracted yet.</p>
            )}
          </CardContent>
        </Card>

        {/* Potential Research Gaps */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between w-full">
              <div className="flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-amber-600" />
                <CardTitle className="text-sm font-semibold">Potential Research Gaps</CardTitle>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onSelectTab('discoveries')}
                className="text-xs text-amber-700 hover:text-amber-800"
              >
                View Discoveries <ArrowRight className="w-3.5 h-3.5 ml-1" />
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {overview.primaryGaps && overview.primaryGaps.length > 0 ? (
              overview.primaryGaps.map((gap, idx) => (
                <div key={idx} className="flex items-start gap-2.5 p-3 rounded-lg bg-amber-50/50 border border-amber-200/60 text-xs text-amber-950">
                  <span className="w-5 h-5 rounded-full bg-amber-200 text-amber-900 font-mono text-[10px] font-bold flex items-center justify-center flex-shrink-0 mt-0.5">
                    G{idx + 1}
                  </span>
                  <p className="leading-relaxed">{gap}</p>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-400">No gaps detected yet.</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Callout to Hypotheses */}
      <div className="p-5 rounded-xl bg-gradient-to-r from-scientific-600 to-indigo-700 text-white flex flex-col sm:flex-row items-center justify-between gap-4 shadow-sm">
        <div className="space-y-1 text-center sm:text-left">
          <div className="flex items-center justify-center sm:justify-start gap-2">
            <Sparkles className="w-4 h-4 text-amber-300" />
            <h4 className="text-sm font-semibold">{stats.hypothesesFormulated || 2} Formulated Hypotheses Ready for Review</h4>
          </div>
          <p className="text-xs text-scientific-100 max-w-xl">
            Inspect falsifiable experimental setups, measurable independent/dependent variables, and rigorous critical counterarguments.
          </p>
        </div>
        <Button
          variant="secondary"
          size="md"
          onClick={() => onSelectTab('hypotheses')}
          icon={ArrowRight}
          iconPosition="right"
          className="bg-white text-scientific-800 hover:bg-scientific-50 shadow-sm"
        >
          Review Hypotheses
        </Button>
      </div>
    </div>
  );
};

