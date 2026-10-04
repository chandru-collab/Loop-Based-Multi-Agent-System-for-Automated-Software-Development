import React, { useState } from 'react';
import { api } from '../services/api';
import { Download, Package, Copy, Check, Sparkles, FolderArchive, Hash, CheckCircle2 } from 'lucide-react';

interface CompletedCelebrationProps {
  projectId: string;
  packageInfo: any;
  onNavigateTab?: (tab: string) => void;
}

export const CompletedCelebration: React.FC<CompletedCelebrationProps> = ({
  projectId,
  packageInfo,
  onNavigateTab,
}) => {
  const [copied, setCopied] = useState(false);
  if (!packageInfo) return null;

  const downloadUrl = api.getDownloadUrl(projectId);
  const sizeMb = packageInfo.package_size
    ? (packageInfo.package_size / 1024 / 1024).toFixed(2)
    : '?';

  const copySha = () => {
    if (packageInfo.checksum_sha256) {
      navigator.clipboard.writeText(packageInfo.checksum_sha256);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="glass-panel rounded-2xl border border-emerald-500/40 bg-emerald-950/20 p-5 shadow-subtle-card space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm sm:text-base font-bold text-emerald-200">
                Software Build Complete & Packaged
              </h2>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                Production Ready
              </span>
            </div>
            <p className="text-xs text-slate-300 mt-0.5">
              All multi-agent stages, test suites, and documentation passes have been verified and sealed in an archive.
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2 self-start sm:self-auto shrink-0">
          <a
            href={api.getPreviewUrl(projectId)}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs shadow-sm active:scale-[0.98] transition-all"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Open Live App</span>
          </a>
          <a
            href={downloadUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs shadow-sm active:scale-[0.98] transition-all"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download ZIP</span>
          </a>
        </div>
      </div>

      {/* Package Metadata Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5">
        <div className="p-2.5 rounded-xl border border-slate-800 bg-slate-900/60">
          <div className="flex items-center gap-1.5 text-slate-400 text-[10px] mb-1">
            <Package className="w-3 h-3 text-emerald-400" />
            <span>Archive Filename</span>
          </div>
          <div className="font-mono text-xs text-slate-200 truncate" title={packageInfo.package_filename}>
            {packageInfo.package_filename}
          </div>
        </div>

        <div className="p-2.5 rounded-xl border border-slate-800 bg-slate-900/60">
          <div className="flex items-center gap-1.5 text-slate-400 text-[10px] mb-1">
            <FolderArchive className="w-3 h-3 text-teal-400" />
            <span>Total Package Size</span>
          </div>
          <div className="font-mono text-xs text-slate-200 font-semibold">{sizeMb} MB</div>
        </div>

        <div className="p-2.5 rounded-xl border border-slate-800 bg-slate-900/60">
          <div className="flex items-center gap-1.5 text-slate-400 text-[10px] mb-1">
            <Sparkles className="w-3 h-3 text-sky-400" />
            <span>Generated Timestamp</span>
          </div>
          <div className="text-xs text-slate-200">
            {packageInfo.created_at ? new Date(packageInfo.created_at).toLocaleString() : 'Just now'}
          </div>
        </div>

        {/* SHA 256 Hash with copy */}
        <div className="p-2.5 rounded-xl border border-slate-800 bg-slate-900/60 col-span-full flex items-center justify-between gap-3">
          <div className="min-w-0">
            <div className="flex items-center gap-1.5 text-slate-400 text-[10px] mb-0.5">
              <Hash className="w-3 h-3 text-indigo-400" />
              <span>SHA-256 Checksum Integrity</span>
            </div>
            <div className="font-mono text-[11px] text-slate-300 truncate">
              {packageInfo.checksum_sha256 || 'Calculated during build packaging'}
            </div>
          </div>
          <button
            onClick={copySha}
            className="flex items-center gap-1 text-xs px-2.5 py-1 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 shrink-0 transition-all"
            title="Copy SHA-256"
          >
            {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>
        </div>
      </div>

      {/* Quick Navigation Pills */}
      <div className="flex flex-wrap items-center gap-1.5 pt-1">
        <span className="text-[11px] text-slate-400">Quick explore:</span>
        {[
          { label: 'Evaluation Metrics', tab: 'evaluation' },
          { label: 'Generated Code Files', tab: 'code' },
          { label: 'Agent Logs', tab: 'agents' },
          { label: 'Iteration Matrix', tab: 'iterations' },
          { label: 'Version History', tab: 'versions' },
        ].map((item) => (
          <button
            key={item.tab}
            onClick={() => onNavigateTab?.(item.tab)}
            className="text-[11px] px-2.5 py-1 rounded-md bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 transition-all flex items-center gap-1"
          >
            <span>{item.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

