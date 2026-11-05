import React, { useState } from 'react';
import { ArrowRight, Sparkles, Layers, BookOpen, AlertCircle } from 'lucide-react';
import { Button } from '../common/Button';
import { Card } from '../common/Card';
import { DocumentUpload } from './DocumentUpload';
import { RESEARCH_DOMAINS, RESEARCH_SCOPES } from '../../utils/constants';

export const ResearchInput = ({ onSubmit, isLoading }) => {
  const [question, setQuestion] = useState('');
  const [domain, setDomain] = useState('');
  const [scope, setScope] = useState('comprehensive');
  const [files, setFiles] = useState([]);
  const [validationError, setValidationError] = useState('');

  const samplePrompts = [
    "How does microglial TREM2 signaling modulate tau spreading in early-stage Alzheimer's?",
    "Why do 2D/3D hybrid perovskite solar cells suffer phase segregation under light soaking?",
    "Can prime editing efficiency in hematopoiesis be decoupled from nick-mediated indels?"
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!question.trim()) {
      setValidationError('Please enter a research question or inquiry.');
      return;
    }
    if (question.trim().length < 12) {
      setValidationError('Please enter a specific research question (at least 12 characters).');
      return;
    }

    setValidationError('');
    onSubmit({
      question: question.trim(),
      domain: domain ? RESEARCH_DOMAINS.find(d => d.id === domain)?.label : 'Cross-Disciplinary',
      domainId: domain || 'cross-disciplinary',
      scope: RESEARCH_SCOPES.find(s => s.id === scope)?.label || 'Comprehensive Synthesis',
      scopeId: scope,
      files,
    });
  };

  const setSample = (prompt) => {
    setQuestion(prompt);
    setValidationError('');
  };

  return (
    <Card id="research-input" className="p-6 sm:p-8 max-w-4xl mx-auto border-slate-200/90 shadow-md">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Research Question */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label htmlFor="research-question" className="text-xs font-semibold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
              <span>Scientific Research Question</span>
              <span className="text-rose-500">*</span>
            </label>
            <span className="text-[11px] text-slate-400 font-mono">
              {question.length} chars
            </span>
          </div>

          <textarea
            id="research-question"
            rows={4}
            value={question}
            onChange={(e) => {
              setQuestion(e.target.value);
              if (validationError) setValidationError('');
            }}
            placeholder="Formulate your core scientific problem (e.g., 'What molecular mechanisms explain the differential efficacy of GLP-1 receptor agonists in non-alcoholic steatohepatitis?')"
            className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-scientific-500 focus:ring-2 focus:ring-scientific-100 text-sm text-slate-900 placeholder:text-slate-400 resize-none transition-all outline-none"
          />

          {validationError && (
            <div className="mt-2 flex items-center gap-1.5 text-xs text-rose-600">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{validationError}</span>
            </div>
          )}

          {/* Quick sample prompt suggestions */}
          <div className="mt-2.5 flex items-center gap-1.5 flex-wrap">
            <span className="text-[11px] text-slate-400 flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-amber-500" />
              Suggestions:
            </span>
            {samplePrompts.map((sample, i) => (
              <button
                key={i}
                type="button"
                onClick={() => setSample(sample)}
                className="text-[11px] text-slate-600 hover:text-scientific-700 bg-slate-100 hover:bg-scientific-50 px-2 py-0.5 rounded-md transition-colors border border-slate-200/60 truncate max-w-[280px]"
              >
                {sample}
              </button>
            ))}
          </div>
        </div>

        {/* Domain & Scope selection */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
          <div>
            <label htmlFor="domain-select" className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-slate-400" />
              <span>Research Domain</span>
              <span className="text-[11px] font-normal text-slate-400 capitalize">(Optional)</span>
            </label>
            <select
              id="domain-select"
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-lg border border-slate-200 bg-white text-xs text-slate-800 focus:border-scientific-500 focus:ring-2 focus:ring-scientific-100 transition-all outline-none"
            >
              <option value="">Select Domain (or auto-detect)</option>
              {RESEARCH_DOMAINS.map(d => (
                <option key={d.id} value={d.id}>{d.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="scope-select" className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <BookOpen className="w-3.5 h-3.5 text-slate-400" />
              <span>Exploration Scope</span>
            </label>
            <select
              id="scope-select"
              value={scope}
              onChange={(e) => setScope(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-lg border border-slate-200 bg-white text-xs text-slate-800 focus:border-scientific-500 focus:ring-2 focus:ring-scientific-100 transition-all outline-none"
            >
              {RESEARCH_SCOPES.map(s => (
                <option key={s.id} value={s.id}>{s.label} — {s.desc}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Supporting Document Upload */}
        <DocumentUpload files={files} onFilesChange={setFiles} />

        {/* Submit Button */}
        <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-4 border-t border-slate-100">
          <p className="text-xs text-slate-500 text-center sm:text-left">
            Launches multi-agent evidence synthesis, gap detection & hypothesis formulation.
          </p>
          <Button
            type="submit"
            size="lg"
            variant="primary"
            isLoading={isLoading}
            icon={ArrowRight}
            iconPosition="right"
            className="w-full sm:w-auto min-w-[190px]"
          >
            Start Research
          </Button>
        </div>
      </form>
    </Card>
  );
};

