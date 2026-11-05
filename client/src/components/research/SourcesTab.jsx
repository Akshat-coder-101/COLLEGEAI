import React, { useState } from 'react';
import { ExternalLink, Quote, Search, BookOpen, CheckCircle, FileText } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import { Badge } from '../common/Badge';
import { Button } from '../common/Button';
import { EmptyState } from '../common/EmptyState';

export const SourcesTab = ({ sources = [] }) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredSources = sources.filter(src => {
    const q = searchTerm.toLowerCase();
    return (
      src.title?.toLowerCase().includes(q) ||
      src.authors?.toLowerCase().includes(q) ||
      src.journal?.toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-6">
      {/* Top search & metadata bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Filter papers by title, author, or journal..."
            className="w-full pl-9 pr-4 py-2 rounded-lg border border-slate-200 bg-white text-xs text-slate-800 placeholder:text-slate-400 focus:outline-none focus:border-scientific-500 focus:ring-1 focus:ring-scientific-500 transition-all"
          />
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-500 font-mono">
          <span>{filteredSources.length} of {sources.length} sources</span>
        </div>
      </div>

      {filteredSources.length === 0 ? (
        <Card className="p-8">
          <EmptyState
            icon={BookOpen}
            title="No matching sources found"
            description="Try modifying your search filter or clear the input to review all indexed literature."
            actionLabel="Clear Filter"
            onAction={() => setSearchTerm('')}
          />
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredSources.map((source, idx) => (
            <Card key={source.id || idx} className="overflow-hidden border-slate-200/90 shadow-sm hover:border-slate-300">
              {/* Header */}
              <div className="p-5 border-b border-slate-100 bg-slate-50/40">
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                  <div className="space-y-1.5 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-mono text-xs font-semibold px-2 py-0.5 rounded bg-slate-200/80 text-slate-700">
                        [{idx + 1}]
                      </span>
                      {source.year && (
                        <Badge variant="default" size="sm">
                          {source.year}
                        </Badge>
                      )}
                      {source.journal && (
                        <span className="text-xs font-medium text-slate-500 italic">
                          {source.journal}
                        </span>
                      )}
                      {source.relevanceScore && (
                        <Badge variant="success" size="sm">
                          {(source.relevanceScore * 100).toFixed(0)}% Relevance
                        </Badge>
                      )}
                    </div>

                    <h3 className="text-base font-semibold text-slate-900 leading-snug">
                      {source.title}
                    </h3>

                    <p className="text-xs text-slate-600">
                      {source.authors}
                    </p>
                  </div>

                  {/* External links */}
                  <div className="flex items-center gap-2 flex-shrink-0 pt-1">
                    {source.doi && (
                      <a
                        href={source.url || `https://doi.org/${source.doi}`}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <Button variant="secondary" size="sm" icon={ExternalLink} iconPosition="right">
                          <span className="font-mono text-[11px]">DOI: {source.doi}</span>
                        </Button>
                      </a>
                    )}
                  </div>
                </div>

                {/* Methodology note */}
                {source.methodology && (
                  <div className="mt-3 p-2.5 rounded bg-white border border-slate-200/70 text-xs text-slate-600">
                    <span className="font-semibold text-slate-800">Methodology: </span>
                    {source.methodology}
                  </div>
                )}
              </div>

              {/* Extracted findings & quotes */}
              <div className="p-5 space-y-4">
                {/* Findings */}
                {source.extractedFindings && source.extractedFindings.length > 0 && (
                  <div>
                    <h4 className="text-xs font-semibold text-slate-800 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                      <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
                      <span>Extracted Empirical Findings</span>
                    </h4>
                    <ul className="space-y-1.5">
                      {source.extractedFindings.map((finding, fIdx) => (
                        <li key={fIdx} className="text-xs text-slate-700 flex items-start gap-2 bg-slate-50 p-2 rounded border border-slate-100">
                          <span className="text-scientific-600 font-bold">•</span>
                          <span>{finding}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Supporting Quotes with page references */}
                {source.supportingQuotes && source.supportingQuotes.length > 0 && (
                  <div>
                    <h4 className="text-xs font-semibold text-slate-800 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                      <Quote className="w-3.5 h-3.5 text-scientific-600" />
                      <span>Verbatim Evidence & Citations</span>
                    </h4>
                    <div className="space-y-2">
                      {source.supportingQuotes.map((q, qIdx) => (
                        <blockquote
                          key={qIdx}
                          className="border-l-2 border-scientific-500 bg-scientific-50/40 p-3 rounded-r-lg text-xs text-slate-800 italic space-y-1"
                        >
                          <p>"{q.quote}"</p>
                          {q.page && (
                            <footer className="not-italic text-[11px] font-mono font-medium text-scientific-700 text-right">
                              — {q.page}
                            </footer>
                          )}
                        </blockquote>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

