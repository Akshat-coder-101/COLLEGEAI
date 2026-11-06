import React, { useState } from 'react';
import {
  ArrowRight,
  Sparkles,
  Layers,
  BookOpen,
  AlertCircle,
  Cpu,
  FlaskConical,
  ShieldCheck,
  Lock,
  EyeOff,
  FileText
} from 'lucide-react';
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

  // Simulation Demands & Requirement State
  const [enableSimulation, setEnableSimulation] = useState(true);
  const [simParadigm, setSimParadigm] = useState('auto');
  const [simInitialState, setSimInitialState] = useState('');
  const [simConstraint, setSimConstraint] = useState('');
  const [simFocusNotes, setSimFocusNotes] = useState('');

  // Confidential Research & Data Privacy Layer State
  const [isConfidential, setIsConfidential] = useState(false);
  const [privacyLevel, setPrivacyLevel] = useState('standard');

  const samplePrompts = [
    "Resource Optimization and Energy Optimization across High-Performance Computing Clusters using Dynamic Voltage and Frequency Scaling",
    "Why do 2D/3D hybrid perovskite solar cells suffer phase segregation under light soaking?",
    "How does microglial TREM2 signaling modulate tau spreading in early-stage Alzheimer's?",
    "What are the ethical and legal implications of autonomous AI copyright in patent law?"
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

    const simulationDemands = enableSimulation ? {
      paradigm: simParadigm,
      initial_state: simInitialState ? parseFloat(simInitialState) : undefined,
      constraint_value: simConstraint ? parseFloat(simConstraint) : undefined,
      focus_notes: simFocusNotes.trim() || undefined,
      // Map to standard scientific model params
      y0: simInitialState ? parseFloat(simInitialState) : undefined,
      frequency_ghz: simInitialState ? parseFloat(simInitialState) : undefined,
      Ea: simConstraint ? parseFloat(simConstraint) : undefined,
      voltage: simConstraint ? parseFloat(simConstraint) : undefined,
    } : null;

    onSubmit({
      question: question.trim(),
      domain: domain ? RESEARCH_DOMAINS.find(d => d.id === domain)?.label : 'Cross-Disciplinary',
      domainId: domain || 'cross-disciplinary',
      scope: RESEARCH_SCOPES.find(s => s.id === scope)?.label || 'Comprehensive Synthesis',
      scopeId: scope,
      enableSimulation,
      simulationDemands,
      isConfidential,
      privacyLevel: isConfidential ? 'confidential' : 'standard',
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
            placeholder="Formulate your core scientific problem (e.g., 'Resource Optimization and Energy Optimization across High-Performance Computing Clusters using Dynamic Voltage and Frequency Scaling')"
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

        {/* Simulation Model Requirement & Dynamic Demand Section */}
        <div className="pt-3 border-t border-slate-100 space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-2">
                <Cpu className="w-4 h-4 text-scientific-600" />
                <span className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                  Computational In Silico Simulation Model
                </span>
              </div>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Option to formulate and numerically solve ODE physical models with SciPy / NumPy
              </p>
            </div>

            {/* Toggle: Required / Not Required */}
            <div className="inline-flex p-1 rounded-lg bg-slate-100 border border-slate-200">
              <button
                type="button"
                onClick={() => setEnableSimulation(true)}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                  enableSimulation
                    ? 'bg-scientific-600 text-white shadow-xs font-semibold'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Required (Active)
              </button>
              <button
                type="button"
                onClick={() => setEnableSimulation(false)}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                  !enableSimulation
                    ? 'bg-slate-700 text-white shadow-xs font-semibold'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Not Required
              </button>
            </div>
          </div>

          {/* Demanded Simulation Inputs (Expands when Required is selected) */}
          {enableSimulation ? (
            <div className="p-4 rounded-xl border border-scientific-200 bg-gradient-to-b from-scientific-50/50 via-white to-white space-y-4 animate-in fade-in duration-200 shadow-2xs">
              <div className="flex items-center justify-between border-b border-scientific-100 pb-2">
                <div className="flex items-center gap-2">
                  <FlaskConical className="w-4 h-4 text-scientific-700" />
                  <span className="text-xs font-bold text-scientific-950 uppercase tracking-wider">
                    Demanding Simulation Inputs (User Specification)
                  </span>
                </div>
                <span className="text-[11px] font-mono text-scientific-700 font-medium">
                  Zero-API • SciPy LSODA ODE Solver
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">
                    Demanded Simulation Paradigm
                  </label>
                  <select
                    value={simParadigm}
                    onChange={(e) => setSimParadigm(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-200 bg-white text-xs text-slate-800 focus:border-scientific-500 focus:ring-1 focus:ring-scientific-200 outline-none"
                  >
                    <option value="auto">Auto-Detect from Research Question (Recommended)</option>
                    <option value="computing_energy">Computing: DVFS Energy & Queueing Latency (P = C·V²·f)</option>
                    <option value="materials_electrochemistry">Electrochemistry & Batteries: Butler-Volmer & Arrhenius</option>
                    <option value="biomedical_pk">Biomedical: Two-Compartment Michaelis-Menten Clearance</option>
                    <option value="physics_dynamical">Physics: Damped Harmonic Oscillator & Dissipation</option>
                  </select>
                </div>

                <div>
                  <label className="block font-semibold text-slate-700 mb-1">
                    Initial State / Operating Amplitude (Y₀ / f₀ / C₀)
                  </label>
                  <input
                    type="number"
                    step="any"
                    value={simInitialState}
                    onChange={(e) => setSimInitialState(e.target.value)}
                    placeholder="e.g. 100 (% or mg/L) or 2.4 (GHz for computing)"
                    className="w-full px-3 py-2 rounded-lg border border-slate-200 bg-white text-xs text-slate-800 focus:border-scientific-500 focus:ring-1 focus:ring-scientific-200 outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">
                    Key Boundary Constraint / Variable (Eₐ, Voltage V, or kₑ)
                  </label>
                  <input
                    type="number"
                    step="any"
                    value={simConstraint}
                    onChange={(e) => setSimConstraint(e.target.value)}
                    placeholder="e.g. 14850 (J/mol) or 1.1 (V for computing)"
                    className="w-full px-3 py-2 rounded-lg border border-slate-200 bg-white text-xs text-slate-800 focus:border-scientific-500 focus:ring-1 focus:ring-scientific-200 outline-none"
                  />
                </div>

                <div>
                  <label className="block font-semibold text-slate-700 mb-1">
                    Demanded Simulation Focus / Hypothesis Note
                  </label>
                  <input
                    type="text"
                    value={simFocusNotes}
                    onChange={(e) => setSimFocusNotes(e.target.value)}
                    placeholder="e.g. Dynamic power reduction under variable Poisson arrival rates"
                    className="w-full px-3 py-2 rounded-lg border border-slate-200 bg-white text-xs text-slate-800 focus:border-scientific-500 focus:ring-1 focus:ring-scientific-200 outline-none"
                  />
                </div>
              </div>

              <div className="p-2.5 rounded-lg bg-amber-50/70 border border-amber-200/80 text-[11px] text-amber-900 leading-relaxed flex items-start gap-2">
                <AlertCircle className="w-3.5 h-3.5 text-amber-600 flex-shrink-0 mt-0.5" />
                <span>
                  <strong>Scientific Validation Honesty:</strong> If your scientific inquiry is qualitative, philosophical, legal, or non-computational, the engine will state directly <em>&quot;Not Possible to Test&quot;</em> without generating synthetic formulas, preserving PRD 01 scientific integrity.
                </span>
              </div>
            </div>
          ) : (
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-600">
              <strong>In Silico Simulation Disabled:</strong> The workflow will focus solely on literature ingestion, empirical extraction, cross-domain connection, and hypothesis formulation without generating computational sandbox models.
            </div>
          )}
        </div>

        {/* Research Data Privacy & Confidential IP Shield Layer */}
        <div className="pt-3 border-t border-slate-100 space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                <span className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                  Confidential Research IP &amp; Privacy Shield
                </span>
                <span className="text-[10px] bg-emerald-50 text-emerald-700 font-mono font-semibold px-2 py-0.5 rounded-full border border-emerald-200">
                  Privacy Layer
                </span>
              </div>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Protects confidential research papers, unpublished patent claims &amp; proprietary compound codes from AI data leakage
              </p>
            </div>

            {/* Toggle: Standard vs Confidential Shield */}
            <div className="inline-flex p-1 rounded-lg bg-slate-100 border border-slate-200">
              <button
                type="button"
                onClick={() => {
                  setIsConfidential(false);
                  setPrivacyLevel('standard');
                }}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                  !isConfidential
                    ? 'bg-slate-700 text-white shadow-xs font-semibold'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Standard Research
              </button>
              <button
                type="button"
                onClick={() => {
                  setIsConfidential(true);
                  setPrivacyLevel('confidential');
                }}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all flex items-center gap-1.5 ${
                  isConfidential
                    ? 'bg-emerald-600 text-white shadow-xs font-semibold'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <Lock className="w-3 h-3" />
                <span>Confidential IP Shield</span>
              </button>
            </div>
          </div>

          {/* Expanded Privacy Layer Details when Confidential is selected */}
          {isConfidential && (
            <div className="p-4 rounded-xl border border-emerald-200 bg-gradient-to-b from-emerald-50/50 via-white to-white space-y-3 animate-in fade-in duration-200 shadow-2xs">
              <div className="flex items-center justify-between border-b border-emerald-100 pb-2">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-emerald-700" />
                  <span className="text-xs font-bold text-emerald-950 uppercase tracking-wider">
                    Confidential IP Safeguards Active
                  </span>
                </div>
                <span className="text-[10px] font-mono text-emerald-700 font-semibold bg-emerald-100/70 px-2 py-0.5 rounded">
                  Zero-Leakage Enforcement
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                <div className="p-2.5 rounded-lg bg-white border border-emerald-100 space-y-1">
                  <span className="font-semibold text-slate-800 flex items-center gap-1">
                    <FileText className="w-3.5 h-3.5 text-emerald-600" />
                    PII &amp; Token Redaction
                  </span>
                  <p className="text-[11px] text-slate-600 leading-snug">
                    Automatically redacts researcher emails, grant IDs, institutional affiliations, and patent serial numbers before LLM ingestion.
                  </p>
                </div>

                <div className="p-2.5 rounded-lg bg-white border border-emerald-100 space-y-1">
                  <span className="font-semibold text-slate-800 flex items-center gap-1">
                    <EyeOff className="w-3.5 h-3.5 text-indigo-600" />
                    Query Leak Prevention
                  </span>
                  <p className="text-[11px] text-slate-600 leading-snug">
                    Sanitizes external literature queries to ensure proprietary project codenames or internal chemical markers are never sent to public APIs.
                  </p>
                </div>

                <div className="p-2.5 rounded-lg bg-white border border-emerald-100 space-y-1">
                  <span className="font-semibold text-slate-800 flex items-center gap-1">
                    <Cpu className="w-3.5 h-3.5 text-scientific-600" />
                    Air-Gapped Simulation
                  </span>
                  <p className="text-[11px] text-slate-600 leading-snug">
                    All in silico mathematical ODE evaluations execute 100% locally with SciPy/NumPy without network calls.
                  </p>
                </div>
              </div>
            </div>
          )}
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
