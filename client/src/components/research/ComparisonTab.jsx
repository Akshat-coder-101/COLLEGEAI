import React from 'react';
import { Scale, CheckCircle2, AlertTriangle, Layers, BarChart2 } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import { Badge } from '../common/Badge';

export const ComparisonTab = ({ comparisons }) => {
  if (!comparisons) return null;

  const chartData = [
    { paper: 'Leyns (2021)', clearance: 85, toxicity: 15, inflammation: 20 },
    { paper: 'Mathys (2023)', clearance: 30, toxicity: 70, inflammation: 80 },
    { paper: 'Marschallinger (2020)', clearance: 25, toxicity: 75, inflammation: 78 },
    { paper: 'Kirby (2024)', clearance: 40, toxicity: 65, inflammation: 72 },
  ];

  return (
    <div className="space-y-6">
      {/* Comparative Synthesis Header */}
      <Card className="bg-slate-50/70 border-slate-200">
        <CardContent className="py-4">
          <div className="flex items-start gap-3">
            <Scale className="w-5 h-5 text-scientific-600 mt-0.5 flex-shrink-0" />
            <div className="space-y-1">
              <h3 className="text-sm font-semibold text-slate-900">Cross-Study Synthesis</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                {comparisons.summary}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Grid: Consensus vs Contradictions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Agreements */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <CardTitle className="text-sm font-semibold">Consensus Across Studies</CardTitle>
            </div>
            <Badge variant="success" size="sm">{comparisons.agreements?.length || 0} Points</Badge>
          </CardHeader>
          <CardContent className="space-y-3.5">
            {comparisons.agreements?.map((agree, idx) => (
              <div key={idx} className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/70 space-y-2">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-semibold text-slate-900">{agree.topic}</h4>
                </div>
                <p className="text-xs text-slate-600 leading-relaxed">
                  {agree.consensus}
                </p>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {agree.papers?.map((p, pIdx) => (
                    <span key={pIdx} className="text-[10px] font-mono bg-white px-2 py-0.5 rounded border border-slate-200 text-slate-600">
                      {p}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Potential Contradictions & Distinctions */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-600" />
              <CardTitle className="text-sm font-semibold">Identified Contradictions & Nuances</CardTitle>
            </div>
            <Badge variant="warning" size="sm">{comparisons.contradictions?.length || 0} Nuances</Badge>
          </CardHeader>
          <CardContent className="space-y-3.5">
            {comparisons.contradictions?.map((contra, idx) => (
              <div key={idx} className="p-3.5 rounded-xl bg-amber-50/40 border border-amber-200/80 space-y-2.5">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-semibold text-amber-950">{contra.topic}</h4>
                  <Badge variant="warning" size="sm">Context Dependant</Badge>
                </div>
                <div className="text-xs text-slate-700">
                  <span className="font-semibold text-amber-900">Apparent Conflict: </span>
                  {contra.conflict}
                </div>
                <div className="text-xs text-slate-600 bg-white/80 p-2.5 rounded-lg border border-amber-100 space-y-1">
                  <div>
                    <span className="font-semibold text-slate-800">Condition Distinction: </span>
                    {contra.contextDifference}
                  </div>
                  <div className="text-emerald-800 font-medium pt-1 border-t border-slate-100">
                    <span className="font-semibold">Synthesis Resolution: </span>
                    {contra.resolution}
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Recharts Visualization */}
      <Card className="min-w-0 overflow-hidden">
        <CardHeader>
          <div className="flex items-center gap-2">
            <BarChart2 className="w-4 h-4 text-scientific-600" />
            <CardTitle className="text-sm font-semibold">
              Comparative Analytical Metrics (Phagocytic Efficacy vs Toxicity)
            </CardTitle>
          </div>
          <span className="text-xs text-slate-400 font-mono hidden sm:inline">Relative index normalized to 100</span>
        </CardHeader>
        <CardContent className="pt-2 px-2 sm:px-6">
          <div className="h-64 w-full min-w-0">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="paper" tick={{ fontSize: 10, fill: '#475569' }} interval={0} />
                <YAxis tick={{ fontSize: 10, fill: '#475569' }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '12px' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                <Bar dataKey="clearance" name="Clearance Index (%)" fill="#0ea5e9" radius={[4, 4, 0, 0]} />
                <Bar dataKey="toxicity" name="Cellular Toxicity (%)" fill="#f43f5e" radius={[4, 4, 0, 0]} />
                <Bar dataKey="inflammation" name="Inflammatory Cytokines" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Comparison Table */}
      {comparisons.comparisonTable && comparisons.comparisonTable.length > 0 && (
        <Card className="overflow-hidden">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-scientific-600" />
              <CardTitle className="text-sm font-semibold">Side-by-Side Methodological Matrix</CardTitle>
            </div>
          </CardHeader>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs min-w-[600px]">
              <thead>
                <tr className="bg-slate-100/80 border-b border-slate-200 text-slate-700">
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider text-[11px]">Parameter</th>
                  <th className="py-3 px-4 font-semibold">Leyns et al. (2021)</th>
                  <th className="py-3 px-4 font-semibold">Mathys et al. (2023)</th>
                  <th className="py-3 px-4 font-semibold">Marschallinger (2020)</th>
                  <th className="py-3 px-4 font-semibold">Kirby et al. (2024)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {comparisons.comparisonTable.map((row, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/60 transition-colors">
                    <td className="py-3 px-4 font-medium text-slate-900 bg-slate-50/50">{row.parameter}</td>
                    <td className="py-3 px-4 text-slate-600">{row.leyns}</td>
                    <td className="py-3 px-4 text-slate-600">{row.mathys}</td>
                    <td className="py-3 px-4 text-slate-600">{row.marschallinger}</td>
                    <td className="py-3 px-4 text-slate-600">{row.kirby}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
};
