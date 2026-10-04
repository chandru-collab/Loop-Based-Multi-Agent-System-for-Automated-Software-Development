import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { FileCode, Copy, Check, Search, MonitorPlay, Terminal, FileText, Code2, ExternalLink, RotateCw } from 'lucide-react';

interface CodeStudioProps {
  projectId: string;
  files: any[];
  selectedFile: string | null;
  fileContent: string;
  onFileClick: (path: string) => void;
}

export const CodeStudio: React.FC<CodeStudioProps> = ({
  projectId,
  files,
  selectedFile,
  fileContent,
  onFileClick,
}) => {
  const [search, setSearch] = useState('');
  const [copied, setCopied] = useState(false);
  const [viewTab, setViewTab] = useState<'code' | 'preview'>('code');
  const [previewKey, setPreviewKey] = useState(0);

  const filteredFiles = files.filter((f) =>
    f.path.toLowerCase().includes(search.toLowerCase())
  );

  useEffect(() => {
    if (files.length > 0 && !selectedFile) {
      const bestDefault = files.find((f) => f.path === 'main.py' || f.path === 'index.html' || f.path === 'App.tsx' || f.path === 'README.md') || files[0];
      onFileClick(bestDefault.path);
    }
  }, [files, selectedFile, onFileClick]);

  const handleCopy = () => {
    if (fileContent) {
      navigator.clipboard.writeText(fileContent);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const lines = fileContent ? fileContent.split('\n') : [];
  const previewUrl = api.getPreviewUrl(projectId);

  return (
    <div className="glass-panel rounded-2xl border border-slate-800/80 shadow-subtle-card overflow-hidden flex flex-col h-[580px]">
      {/* Top Studio Bar */}
      <div className="p-3 px-4 border-b border-slate-800/80 flex flex-wrap items-center justify-between gap-3 bg-slate-950/60">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5 mr-2">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500/80 inline-block" />
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500/80 inline-block" />
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/80 inline-block" />
          </div>
          <span className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
            <Code2 className="w-3.5 h-3.5 text-indigo-400" />
            Project Code Explorer
          </span>
          <span className="text-[10px] font-mono text-cyan-400 px-2 py-0.5 rounded-md bg-cyan-950/60 border border-cyan-800/40">
            {files.length} Generated Files
          </span>
        </div>

        {/* View Switcher Tabs & Tools */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 bg-slate-900 p-1 rounded-lg border border-slate-800">
            <button
              onClick={() => setViewTab('code')}
              className={`flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-md transition-all ${
                viewTab === 'code' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Terminal className="w-3 h-3" />
              <span>Code Inspector</span>
            </button>
            <button
              onClick={() => setViewTab('preview')}
              className={`flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-md transition-all ${
                viewTab === 'preview' ? 'bg-cyan-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <MonitorPlay className="w-3 h-3" />
              <span>Live App Preview</span>
            </button>
          </div>

          {viewTab === 'preview' && (
            <div className="flex items-center gap-1">
              <button
                onClick={() => setPreviewKey((k) => k + 1)}
                className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 text-xs transition-all"
                title="Reload Preview"
              >
                <RotateCw className="w-3.5 h-3.5" />
              </button>
              <a
                href={previewUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-indigo-950/60 hover:bg-indigo-900/60 text-indigo-300 border border-indigo-700/50 text-xs font-medium transition-all"
                title="Open in new window"
              >
                <ExternalLink className="w-3 h-3" />
                <span className="hidden sm:inline">Pop Out</span>
              </a>
            </div>
          )}
        </div>
      </div>

      {viewTab === 'code' ? (
        <div className="flex flex-1 overflow-hidden">
          {/* File Tree Sidebar */}
          <div className="w-64 border-r border-slate-800/80 bg-slate-950/40 flex flex-col shrink-0">
            {/* Search Input */}
            <div className="p-2 border-b border-slate-800/80">
              <div className="relative">
                <Search className="w-3 h-3 text-slate-500 absolute left-2.5 top-2.5" />
                <input
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Filter files..."
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-7 pr-3 py-1 text-xs text-slate-200 placeholder-slate-500 focus:border-indigo-500 outline-none"
                />
              </div>
            </div>

            {/* File List */}
            <div className="flex-1 overflow-y-auto p-1.5 space-y-0.5">
              {filteredFiles.map((f) => {
                const isSelected = selectedFile === f.path;
                return (
                  <button
                    key={f.path}
                    onClick={() => onFileClick(f.path)}
                    className={`w-full text-left px-2.5 py-1.5 rounded-lg text-xs font-mono truncate flex items-center gap-2 transition-all ${
                      isSelected
                        ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 font-semibold shadow-sm'
                        : 'text-slate-400 hover:bg-slate-900/60 hover:text-slate-200'
                    }`}
                    title={f.path}
                  >
                    <FileText className="w-3.5 h-3.5 shrink-0 text-slate-500" />
                    <span className="truncate">{f.path}</span>
                  </button>
                );
              })}
              {filteredFiles.length === 0 && (
                <div className="text-[11px] text-slate-500 p-4 text-center">No matching files in workspace.</div>
              )}
            </div>
          </div>

          {/* Code Viewer Panel */}
          <div className="flex-1 flex flex-col bg-[#070b14] overflow-hidden">
            {selectedFile ? (
              <>
                {/* File Header Tab */}
                <div className="flex items-center justify-between p-2 px-4 bg-slate-900/60 border-b border-slate-800/80">
                  <div className="flex items-center gap-2 font-mono text-xs text-slate-300">
                    <span className="text-sky-400 font-semibold">{selectedFile}</span>
                    <span className="text-slate-500">· {lines.length} lines</span>
                  </div>
                  <button
                    onClick={handleCopy}
                    className="flex items-center gap-1.5 text-xs text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 px-2 py-1 rounded-md border border-slate-700 transition-all"
                  >
                    {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                    <span>{copied ? 'Copied' : 'Copy'}</span>
                  </button>
                </div>

                {/* Code Content with Line Numbers */}
                <div className="flex-1 overflow-auto p-3 font-mono text-xs leading-5 text-slate-200 flex">
                  {/* Line numbers column */}
                  <div className="select-none text-slate-600 pr-3 text-right shrink-0 border-r border-slate-800/60 mr-3">
                    {lines.map((_, i) => (
                      <div key={i}>{i + 1}</div>
                    ))}
                  </div>
                  {/* Code body */}
                  <pre className="whitespace-pre flex-1 text-slate-200 selection:bg-indigo-500/40">
                    {fileContent || '// Empty file or loading contents...'}
                  </pre>
                </div>
              </>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-slate-500 space-y-2 p-6">
                <FileCode className="w-8 h-8 text-slate-600 mb-1" />
                <p className="text-sm font-medium text-slate-400">Select any project file from the left sidebar</p>
                <p className="text-xs text-slate-600">Explore generated endpoints, business logic, schemas, and tests.</p>
              </div>
            )}
          </div>
        </div>
      ) : (
        /* Live App Preview Tab */
        <div className="flex-1 bg-white relative">
          <iframe
            key={previewKey}
            title="Generated App Live Preview"
            src={previewUrl}
            className="w-full h-full border-0"
            sandbox="allow-forms allow-modals allow-popups allow-scripts allow-same-origin"
          />
        </div>
      )}
    </div>
  );
};
