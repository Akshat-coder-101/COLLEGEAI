import React, { useState } from 'react';
import {
  ExternalLink,
  Quote,
  Search,
  BookOpen,
  CheckCircle,
  FileText,
  Download,
  Eye,
  X,
  FileCheck2,
  Sparkles
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import { Badge } from '../common/Badge';
import { Button } from '../common/Button';
import { EmptyState } from '../common/EmptyState';

export const SourcesTab = ({ sources = [] }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPdf, setSelectedPdf] = useState(null);
  const [filterType, setFilterType] = useState('all'); // 'all', 'pdf', 'external'

  const uploadedPdfCount = sources.filter(s => s.isUploadedDoc || s.pdfUrl).length;

  const filteredSources = sources.filter(src => {
    const q = searchTerm.toLowerCase();
    const matchesSearch = (
      src.title?.toLowerCase().includes(q) ||
      src.authors?.toLowerCase().includes(q) ||
      src.journal?.toLowerCase().includes(q)
    );

    if (!matchesSearch) return false;
    if (filterType === 'pdf') return Boolean(src.isUploadedDoc || src.pdfUrl);
    if (filterType === 'external') return !src.isUploadedDoc;
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Top filter bar with PDF counter */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Filter papers by title, author, or methodology..."
            className="w-full pl-9 pr-4 py-2 rounded-lg border border-slate-200 bg-white text-xs text-slate-800 placeholder:text-slate-400 focus:outline-none focus:border-scientific-500 focus:ring-1 focus:ring-scientific-500 transition-all"
          />
        </div>

        <div className="flex items-center gap-2">
          {/* Quick Filter Pills */}
          <div className="inline-flex p-1 rounded-lg bg-slate-100 border border-slate-200 text-xs">
            <button
              onClick={() => setFilterType('all')}
              className={`px-2.5 py-1 rounded-md transition-all ${filterType === 'all' ? 'bg-white font-semibold text-slate-900 shadow-2xs' : 'text-slate-600 hover:text-slate-900'}`}
            >
              All Sources ({sources.length})
            </button>
            <button
              onClick={() => setFilterType('pdf')}
              className={`px-2.5 py-1 rounded-md transition-all flex items-center gap-1 ${filterType === 'pdf' ? 'bg-white font-semibold text-scientific-700 shadow-2xs' : 'text-slate-600 hover:text-slate-900'}`}
            >
              <FileText className="w-3.5 h-3.5 text-scientific-600" />
              <span>PDF Papers ({uploadedPdfCount})</span>
            </button>
          </div>
        </div>
      </div>

      {filteredSources.length === 0 ? (
        <Card className="p-8">
          <EmptyState
            icon={BookOpen}
            title="No matching sources found"
            description="Try modifying your search filter or clear the input to review all indexed literature."
            actionLabel="Reset Filters"
            onAction={() => { setSearchTerm(''); setFilterType('all'); }}
          />
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredSources.map((source, idx) => (
            <Card key={source.id || idx} className="overflow-hidden border-slate-200/90 shadow-sm hover:border-slate-300 transition-all">
              {/* Header */}
              <div className="p-5 border-b border-slate-100 bg-slate-50/50">
                <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-3">
                  <div className="space-y-1.5 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-mono text-xs font-semibold px-2 py-0.5 rounded bg-slate-200/80 text-slate-700">
                        [{idx + 1}]
                      </span>
                      {source.isUploadedDoc ? (
                        <Badge variant="success" size="sm" className="flex items-center gap-1">
                          <FileCheck2 className="w-3 h-3" />
                          <span>Uploaded Research PDF</span>
                        </Badge>
                      ) : (
                        <Badge variant="default" size="sm">
                          Academic Source
                        </Badge>
                      )}
                      {source.year && (
                        <span className="text-xs font-mono text-slate-500">
                          {source.year}
                        </span>
                      )}
                      {source.journal && (
                        <span className="text-xs font-medium text-slate-500 italic">
                          • {source.journal}
                        </span>
                      )}
                      {source.pageCount && (
                        <span className="text-xs font-mono text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-100">
                          {source.pageCount} Pages
                        </span>
                      )}
                    </div>

                    <h3 className="text-base font-semibold text-slate-900 leading-snug">
                      {source.title}
                    </h3>

                    <p className="text-xs text-slate-600 font-medium">
                      {source.authors}
                    </p>
                  </div>

                  {/* Actions: View PDF, Download, External Link */}
                  <div className="flex flex-wrap items-center gap-2 flex-shrink-0 pt-1">
                    {source.pdfUrl && (
                      <button
                        onClick={() => setSelectedPdf(source)}
                        className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-scientific-600 hover:bg-scientific-700 text-white text-xs font-medium shadow-xs transition-colors"
                        title="View Full PDF Paper"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>View PDF</span>
                      </button>
                    )}

                    {source.downloadUrl && (
                      <a
                        href={source.downloadUrl}
                        download
                        className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 text-xs font-medium transition-colors"
                        title="Download Research Paper PDF"
                      >
                        <Download className="w-3.5 h-3.5 text-slate-500" />
                        <span>Download</span>
                      </a>
                    )}

                    {source.doi && source.doi !== 'N/A' && (
                      <a
                        href={source.url || `https://doi.org/${source.doi}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 text-xs font-mono transition-colors"
                      >
                        <span>DOI: {source.doi}</span>
                        <ExternalLink className="w-3 h-3 text-slate-400" />
                      </a>
                    )}
                  </div>
                </div>

                {/* Methodology note */}
                {source.methodology && (
                  <div className="mt-3 p-2.5 rounded-lg bg-white border border-slate-200/70 text-xs text-slate-600">
                    <span className="font-semibold text-slate-800">Methodology &amp; Architecture: </span>
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
                      <span>Extracted Empirical Findings &amp; Numeric Parameters</span>
                    </h4>
                    <ul className="space-y-1.5">
                      {source.extractedFindings.map((finding, fIdx) => (
                        <li key={fIdx} className="text-xs text-slate-700 flex items-start gap-2 bg-slate-50 p-2.5 rounded-lg border border-slate-100">
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
                      <span>Verbatim Document Evidence (Source Traceability)</span>
                    </h4>
                    <div className="space-y-2">
                      {source.supportingQuotes.map((q, qIdx) => (
                        <blockquote
                          key={qIdx}
                          className="border-l-3 border-scientific-500 bg-scientific-50/40 p-3 rounded-r-lg text-xs text-slate-800 italic space-y-1"
                        >
                          <p>&quot;{q.quote}&quot;</p>
                          {q.page && (
                            <footer className="not-italic text-[11px] font-mono font-semibold text-scientific-700 text-right">
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

      {/* MODAL: Full In-App PDF Document Viewer */}
      {selectedPdf && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-slate-900/70 backdrop-blur-xs animate-in fade-in duration-200">
          <div className="bg-white rounded-2xl shadow-2xl max-w-5xl w-full max-h-[92vh] flex flex-col overflow-hidden border border-slate-200">
            {/* Modal Header */}
            <div className="p-4 bg-slate-900 text-white flex items-center justify-between border-b border-slate-800">
              <div className="space-y-1 pr-4">
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-emerald-400" />
                  <span className="text-xs font-mono font-semibold text-emerald-300 uppercase tracking-wider">
                    Research Paper PDF Document Viewer
                  </span>
                  {selectedPdf.pageCount && (
                    <span className="text-[11px] font-mono text-slate-400 bg-slate-800 px-2 py-0.5 rounded">
                      {selectedPdf.pageCount} Pages
                    </span>
                  )}
                </div>
                <h3 className="text-sm font-bold text-slate-100 truncate max-w-2xl">
                  {selectedPdf.title}
                </h3>
              </div>

              <div className="flex items-center gap-2 flex-shrink-0">
                <a
                  href={selectedPdf.pdfUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-2.5 py-1 text-xs font-medium text-slate-200 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-lg flex items-center gap-1 transition-colors"
                  title="Open PDF in new tab"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  <span>Open Tab</span>
                </a>

                {selectedPdf.downloadUrl && (
                  <a
                    href={selectedPdf.downloadUrl}
                    download
                    className="px-2.5 py-1 text-xs font-medium text-slate-200 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-lg flex items-center gap-1 transition-colors"
                    title="Download PDF"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download</span>
                  </a>
                )}

                <button
                  onClick={() => setSelectedPdf(null)}
                  className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors ml-1"
                  title="Close Viewer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Embedded PDF iframe */}
            <div className="flex-1 bg-slate-100 relative min-h-[550px] overflow-hidden">
              <iframe
                src={selectedPdf.pdfUrl}
                title={selectedPdf.title}
                className="w-full h-full min-h-[550px] border-0"
              />
            </div>

            {/* Footer with quick citations */}
            <div className="p-3 bg-slate-50 border-t border-slate-200 text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-slate-600">
              <span className="truncate max-w-xl">
                Authors: <strong className="text-slate-800">{selectedPdf.authors}</strong>
              </span>
              <span className="font-mono text-[11px] text-scientific-700 font-medium">
                Verified Extraction &bull; PyMuPDF Ingested
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
