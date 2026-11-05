import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Microscope, PlusCircle, ArrowLeft } from 'lucide-react';
import { Button } from '../common/Button';
import { DevBadge } from './DevBadge';

export const Navbar = () => {
  const location = useLocation();
  const isWorkspace = location.pathname.startsWith('/research/');

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-sm border-b border-slate-200/80 transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-scientific-600 to-scientific-800 text-white flex items-center justify-center shadow-sm shadow-scientific-500/20 group-hover:scale-105 transition-transform">
              <Microscope className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-semibold text-slate-900 tracking-tight text-base">HypothesisLab</span>
                <span className="text-[10px] font-bold uppercase tracking-wider bg-scientific-50 text-scientific-700 px-1.5 py-0.5 rounded border border-scientific-200">
                  AI
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-normal leading-none hidden sm:block">
                Scientific Hypothesis & Research Discovery
              </p>
            </div>
          </Link>
        </div>

        <div className="flex items-center gap-3">
          <DevBadge />
          {isWorkspace ? (
            <Link to="/">
              <Button variant="secondary" size="sm" icon={ArrowLeft}>
                New Research
              </Button>
            </Link>
          ) : (
            <a href="#research-input">
              <Button variant="primary" size="sm" icon={PlusCircle}>
                Start Exploration
              </Button>
            </a>
          )}
        </div>
      </div>
    </header>
  );
};

