import React from 'react';
import { Sparkles, BookOpenCheck, GitFork, ShieldCheck } from 'lucide-react';

export const HeroSection = () => {
  return (
    <section className="pt-10 pb-8 text-center max-w-4xl mx-auto px-4">
      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium bg-scientific-50 text-scientific-700 border border-scientific-200/80 mb-6 shadow-xs">
        <Sparkles className="w-3.5 h-3.5 text-scientific-600" />
        <span>Autonomous Multi-Agent Scientific Discovery</span>
      </div>

      <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-900 tracking-tight leading-[1.15]">
        Go Beyond Reading Research.{' '}
        <span className="text-scientific-600 underline decoration-scientific-200 underline-offset-4">
          Discover What's Missing.
        </span>
      </h1>

      <p className="mt-4 text-base sm:text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed">
        Analyze scientific literature, uncover potential research gaps, connect ideas across disciplines, and formulate rigorously testable hypotheses with AI.
      </p>

      {/* Scientific pillars */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-8 pt-6 border-t border-slate-200/60 max-w-3xl mx-auto text-left">
        <div className="flex items-start gap-2.5 p-2 rounded-lg bg-slate-50/70">
          <BookOpenCheck className="w-4 h-4 text-scientific-600 mt-0.5 flex-shrink-0" />
          <div>
            <div className="text-xs font-semibold text-slate-800">Evidence Extraction</div>
            <div className="text-[11px] text-slate-500">Grounded paper citations & claims</div>
          </div>
        </div>

        <div className="flex items-start gap-2.5 p-2 rounded-lg bg-slate-50/70">
          <GitFork className="w-4 h-4 text-indigo-600 mt-0.5 flex-shrink-0" />
          <div>
            <div className="text-xs font-semibold text-slate-800">Gap Detection</div>
            <div className="text-[11px] text-slate-500">Uncovered blind spots & conflicts</div>
          </div>
        </div>

        <div className="flex items-start gap-2.5 p-2 rounded-lg bg-slate-50/70">
          <Sparkles className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" />
          <div>
            <div className="text-xs font-semibold text-slate-800">Hypotheses Formulation</div>
            <div className="text-[11px] text-slate-500">Falsifiable variables & methods</div>
          </div>
        </div>

        <div className="flex items-start gap-2.5 p-2 rounded-lg bg-slate-50/70">
          <ShieldCheck className="w-4 h-4 text-emerald-600 mt-0.5 flex-shrink-0" />
          <div>
            <div className="text-xs font-semibold text-slate-800">Critical Review</div>
            <div className="text-[11px] text-slate-500">Counterevidence & limitations</div>
          </div>
        </div>
      </div>
    </section>
  );
};

