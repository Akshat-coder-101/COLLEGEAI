import React, { useState } from 'react';
import { FlaskConical, ChevronDown, ChevronUp, ShieldCheck, AlertCircle, CheckCircle2, Sliders, TestTube, Lightbulb } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import { Badge } from '../common/Badge';
import { Button } from '../common/Button';

export const HypothesesTab = ({ hypotheses = [] }) => {
  const [expandedReviews, setExpandedReviews] = useState({ 0: true });

  const toggleReview = (index) => {
    setExpandedReviews(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <FlaskConical className="w-5 h-5 text-scientific-600" />
            <span>Formulated Testable Hypotheses</span>
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Falsifiable claims derived from cross-study gaps, complete with experimental designs and critical reviews
          </p>
        </div>
        <Badge variant="indigo" size="sm">{hypotheses.length} Hypotheses Formulated</Badge>
      </div>

      <div className="space-y-6">
        {hypotheses.map((hypo, idx) => {
          const isReviewOpen = !!expandedReviews[idx];

          return (
            <Card key={hypo.id || idx} className="border-slate-200/90 shadow-sm overflow-hidden">
              {/* Header */}
              <div className="p-5 bg-slate-50/60 border-b border-slate-100">
                <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                  <span className="text-xs font-mono font-bold text-scientific-700 bg-scientific-50 px-2.5 py-0.5 rounded border border-scientific-200">
                    HYPOTHESIS #{idx + 1}
                  </span>
                  {hypo.gapAddressed && (
                    <span className="text-xs text-slate-500 flex items-center gap-1">
                      <span className="font-semibold text-slate-700">Addresses: </span>
                      <span className="italic">{hypo.gapAddressed}</span>
                    </span>
                  )}
                </div>

                <h3 className="text-base sm:text-lg font-semibold text-slate-900 leading-snug">
                  "{hypo.statement}"
                </h3>
              </div>

              <div className="p-5 space-y-5">
                {/* Variables Grid */}
                {hypo.variables && (
                  <div>
                    <h4 className="text-xs font-semibold text-slate-800 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                      <Sliders className="w-3.5 h-3.5 text-scientific-600" />
                      <span>Operational Variables</span>
                    </h4>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                      <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/70 text-xs">
                        <span className="font-semibold text-scientific-700 uppercase tracking-wider text-[10px] block mb-1">
                          Independent Variable
                        </span>
                        <p className="text-slate-800">{hypo.variables.independent}</p>
                      </div>

                      <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/70 text-xs">
                        <span className="font-semibold text-emerald-700 uppercase tracking-wider text-[10px] block mb-1">
                          Dependent Variable
                        </span>
                        <p className="text-slate-800">{hypo.variables.dependent}</p>
                      </div>

                      <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/70 text-xs">
                        <span className="font-semibold text-slate-600 uppercase tracking-wider text-[10px] block mb-1">
                          Control Conditions
                        </span>
                        <p className="text-slate-800">{hypo.variables.control}</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Suggested Experiment & Falsification Criteria */}
                {hypo.suggestedExperiment && (
                  <div className="p-4 rounded-xl bg-scientific-50/40 border border-scientific-200/80 space-y-3">
                    <h4 className="text-xs font-semibold text-scientific-950 uppercase tracking-wider flex items-center gap-1.5">
                      <TestTube className="w-4 h-4 text-scientific-600" />
                      <span>Suggested Experimental Protocol</span>
                    </h4>

                    <div className="text-xs text-slate-800 leading-relaxed">
                      <span className="font-semibold text-slate-900">Methodology: </span>
                      {hypo.suggestedExperiment.methodology}
                    </div>

                    <div className="text-xs text-slate-800 leading-relaxed">
                      <span className="font-semibold text-slate-900">Primary Measurements: </span>
                      {hypo.suggestedExperiment.measurements}
                    </div>

                    {hypo.suggestedExperiment.falsificationCriteria && (
                      <div className="text-xs text-rose-900 bg-white/80 p-2.5 rounded-lg border border-rose-200/80">
                        <span className="font-semibold text-rose-800">Falsification Threshold: </span>
                        {hypo.suggestedExperiment.falsificationCriteria}
                      </div>
                    )}
                  </div>
                )}

                {/* Supporting Evidence vs Counterarguments */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="text-xs font-semibold text-slate-800 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                      <span>Supporting Evidence</span>
                    </h4>
                    <ul className="space-y-1.5 text-xs text-slate-700">
                      {hypo.supportingEvidence?.map((ev, eIdx) => (
                        <li key={eIdx} className="p-2 rounded bg-slate-50 border border-slate-100 flex items-start gap-2">
                          <span className="text-emerald-600 font-bold">•</span>
                          <span>{ev}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h4 className="text-xs font-semibold text-slate-800 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                      <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
                      <span>Counterarguments & Confounders</span>
                    </h4>
                    <ul className="space-y-1.5 text-xs text-slate-700">
                      {hypo.counterarguments?.map((ca, cIdx) => (
                        <li key={cIdx} className="p-2 rounded bg-amber-50/40 border border-amber-100 flex items-start gap-2">
                          <span className="text-amber-600 font-bold">•</span>
                          <span>{ca}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Expandable Critical Review Section */}
                {hypo.criticalReview && (
                  <div className="border border-slate-200 rounded-xl overflow-hidden">
                    <button
                      type="button"
                      onClick={() => toggleReview(idx)}
                      className="w-full px-4 py-3 bg-slate-50 hover:bg-slate-100/80 flex items-center justify-between text-left transition-colors"
                    >
                      <div className="flex items-center gap-2">
                        <ShieldCheck className="w-4 h-4 text-indigo-600" />
                        <span className="text-xs font-semibold text-slate-800">
                          Critical Academic Review & Scientific Rigor
                        </span>
                      </div>
                      {isReviewOpen ? (
                        <ChevronUp className="w-4 h-4 text-slate-500" />
                      ) : (
                        <ChevronDown className="w-4 h-4 text-slate-500" />
                      )}
                    </button>

                    {isReviewOpen && (
                      <div className="p-4 bg-white space-y-3 text-xs border-t border-slate-200">
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                          <div className="p-2.5 rounded bg-emerald-50/50 border border-emerald-100">
                            <span className="font-semibold text-emerald-800 block mb-0.5">Strengths</span>
                            <p className="text-slate-700">{hypo.criticalReview.strengths}</p>
                          </div>
                          <div className="p-2.5 rounded bg-rose-50/50 border border-rose-100">
                            <span className="font-semibold text-rose-800 block mb-0.5">Known Weaknesses</span>
                            <p className="text-slate-700">{hypo.criticalReview.weaknesses}</p>
                          </div>
                        </div>

                        <div className="p-2.5 rounded bg-slate-50 border border-slate-100">
                          <span className="font-semibold text-slate-800 block mb-0.5">Alternative Explanations</span>
                          <p className="text-slate-700">{hypo.criticalReview.alternativeExplanations}</p>
                        </div>

                        <div className="p-2.5 rounded bg-scientific-50/60 border border-scientific-100">
                          <span className="font-semibold text-scientific-900 block mb-0.5">Recommended Refinements</span>
                          <p className="text-slate-700">{hypo.criticalReview.suggestedImprovements}</p>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
};

