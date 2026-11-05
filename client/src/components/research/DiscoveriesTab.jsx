import React from 'react';
import { Sparkles, Network, GitBranch, ArrowUpRight, ShieldCheck, AlertCircle } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import { Badge } from '../common/Badge';
import { DiscoveryGraph } from '../graph/DiscoveryGraph';

export const DiscoveriesTab = ({ discoveries }) => {
  if (!discoveries) return null;

  const { gaps = [], crossDomainConnections = [], knowledgeGraph } = discoveries;

  return (
    <div className="space-y-6">
      {/* Knowledge Graph Card (React Flow) */}
      {knowledgeGraph && (
        <Card className="border-slate-200 shadow-sm">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Network className="w-4 h-4 text-scientific-600" />
              <CardTitle className="text-sm font-semibold">Interactive Discovery & Relationship Graph</CardTitle>
            </div>
            <span className="text-xs text-slate-500 font-mono">
              {knowledgeGraph.nodes?.length} Entities • {knowledgeGraph.edges?.length} Interconnections
            </span>
          </CardHeader>
          <CardContent className="p-3 sm:p-5">
            <p className="text-xs text-slate-500 mb-3">
              Explore the synthesized mechanistic connections across pathologies, lipid crystallization, and therapeutic interventions.
            </p>
            <DiscoveryGraph graphData={knowledgeGraph} />
          </CardContent>
        </Card>
      )}

      {/* Research Gaps Section */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-base font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-amber-600" />
            <span>Uncovered Research Gaps</span>
          </h3>
          <Badge variant="warning" size="sm">{gaps.length} Gaps Isolated</Badge>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {gaps.map((gap, idx) => (
            <Card key={gap.id || idx} className="p-5 border-slate-200/90 shadow-sm hover:border-amber-300 transition-colors">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-mono font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                    GAP #{idx + 1}
                  </span>
                  {gap.confidence && (
                    <Badge variant="success" size="sm">
                      <ShieldCheck className="w-3 h-3 mr-1 text-emerald-600" />
                      {(gap.confidence * 100).toFixed(0)}% Confidence
                    </Badge>
                  )}
                </div>

                <h4 className="text-sm font-semibold text-slate-900 leading-snug">
                  {gap.title}
                </h4>

                <p className="text-xs text-slate-600 leading-relaxed">
                  {gap.description}
                </p>

                {gap.significance && (
                  <div className="text-[11px] bg-slate-50 p-2.5 rounded-lg border border-slate-100 text-slate-700">
                    <span className="font-semibold text-slate-900">Significance: </span>
                    {gap.significance}
                  </div>
                )}
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Cross-Domain Connections */}
      {crossDomainConnections.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-base font-bold text-slate-900 tracking-tight flex items-center gap-2">
              <GitBranch className="w-4 h-4 text-purple-600" />
              <span>Cross-Disciplinary Connections</span>
            </h3>
            <Badge variant="purple" size="sm">{crossDomainConnections.length} Bridges</Badge>
          </div>

          <div className="space-y-4">
            {crossDomainConnections.map((cdc, idx) => (
              <Card key={cdc.id || idx} className="p-5 border-purple-200/80 bg-purple-50/20 shadow-sm">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-purple-100 pb-3 mb-3">
                  <div className="flex items-center gap-2 text-xs">
                    <span className="font-semibold text-purple-900 bg-purple-100 px-2 py-0.5 rounded">
                      {cdc.sourceField}
                    </span>
                    <span className="text-purple-400">⟶</span>
                    <span className="font-semibold text-scientific-900 bg-scientific-100 px-2 py-0.5 rounded">
                      {cdc.targetField}
                    </span>
                  </div>
                </div>

                <p className="text-xs text-slate-800 leading-relaxed mb-3">
                  {cdc.connection}
                </p>

                {cdc.implication && (
                  <div className="text-xs bg-white p-3 rounded-lg border border-purple-200/60 text-purple-950">
                    <span className="font-semibold text-purple-800">Translational Implication: </span>
                    {cdc.implication}
                  </div>
                )}
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

