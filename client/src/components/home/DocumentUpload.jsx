import React, { useRef } from 'react';
import { UploadCloud, FileText, X, AlertCircle } from 'lucide-react';
import { Button } from '../common/Button';

export const DocumentUpload = ({ files = [], onFilesChange }) => {
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      addFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      addFiles(Array.from(e.target.files));
    }
  };

  const addFiles = (newFiles) => {
    const validPdfs = newFiles.filter(file => file.type === 'application/pdf' || file.name.endsWith('.pdf'));
    const unique = [...files];
    validPdfs.forEach(newF => {
      if (!unique.some(f => f.name === newF.name && f.size === newF.size)) {
        unique.push(newF);
      }
    });
    onFilesChange(unique);
  };

  const removeFile = (index) => {
    const updated = files.filter((_, i) => i !== index);
    onFilesChange(updated);
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-xs font-semibold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
          <span>Supporting Literature / PDFs</span>
          <span className="text-[11px] font-normal text-slate-400 capitalize">(Optional)</span>
        </label>
        {files.length > 0 && (
          <span className="text-xs text-slate-500 font-mono">
            {files.length} {files.length === 1 ? 'file' : 'files'} attached
          </span>
        )}
      </div>

      <div
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className="group relative border-2 border-dashed border-slate-200 hover:border-scientific-400 rounded-xl p-5 text-center cursor-pointer transition-colors bg-slate-50/50 hover:bg-scientific-50/20"
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,application/pdf"
          className="hidden"
          onChange={handleFileInput}
        />
        <div className="flex flex-col items-center justify-center gap-1.5">
          <div className="w-10 h-10 rounded-lg bg-white border border-slate-200 flex items-center justify-center text-slate-500 group-hover:text-scientific-600 group-hover:border-scientific-300 transition-colors shadow-xs">
            <UploadCloud className="w-5 h-5" />
          </div>
          <div className="text-xs font-medium text-slate-700">
            <span className="text-scientific-600 font-semibold group-hover:underline">Click to upload</span> or drag and drop PDFs
          </div>
          <p className="text-[11px] text-slate-400">
            Attach preprints or papers to seed the evidence extractor (PDF only, up to 25MB each)
          </p>
        </div>
      </div>

      {/* Selected file pills */}
      {files.length > 0 && (
        <div className="flex flex-wrap gap-2 pt-1">
          {files.map((file, idx) => (
            <div
              key={`${file.name}-${idx}`}
              className="inline-flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-white border border-slate-200 text-xs text-slate-700 shadow-xs group"
            >
              <FileText className="w-3.5 h-3.5 text-scientific-600 flex-shrink-0" />
              <span className="max-w-[200px] truncate font-medium text-[12px]">{file.name}</span>
              <span className="text-[10px] text-slate-400 font-mono">
                {(file.size / (1024 * 1024)).toFixed(1)}MB
              </span>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  removeFile(idx);
                }}
                className="text-slate-400 hover:text-rose-500 p-0.5 rounded transition-colors"
                title="Remove file"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

