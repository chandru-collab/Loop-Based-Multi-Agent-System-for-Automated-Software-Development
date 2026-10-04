import React, { useState } from 'react';
import { api } from '../services/api';
import { MonitorPlay, RotateCw, ExternalLink, Smartphone, Tablet, Monitor, Sparkles } from 'lucide-react';

interface LiveAppPreviewProps {
  projectId: string;
  projectName?: string;
}

export const LiveAppPreview: React.FC<LiveAppPreviewProps> = ({ projectId, projectName }) => {
  const [device, setDevice] = useState<'desktop' | 'tablet' | 'mobile'>('desktop');
  const [reloadKey, setReloadKey] = useState(0);
  const [isLoading, setIsLoading] = useState(false);

  const previewUrl = api.getPreviewUrl(projectId);

  const handleReload = () => {
    setIsLoading(true);
    setReloadKey((k) => k + 1);
    setTimeout(() => setIsLoading(false), 500);
  };

  const getContainerWidth = () => {
    switch (device) {
      case 'mobile':
        return 'w-[375px] h-[667px] shadow-2xl rounded-3xl border-4 border-slate-800';
      case 'tablet':
        return 'w-[768px] h-[720px] shadow-2xl rounded-2xl border-4 border-slate-800';
      case 'desktop':
      default:
        return 'w-full h-[620px] rounded-xl border border-slate-800';
    }
  };

  return (
    <div className="glass-panel rounded-2xl border border-slate-800/80 shadow-subtle-card overflow-hidden flex flex-col">
      {/* Live Preview Controls Header */}
      <div className="p-3.5 px-4 border-b border-slate-800/80 flex flex-wrap items-center justify-between gap-3 bg-slate-950/70">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
            <MonitorPlay className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-slate-200">Interactive Live App Preview</span>
              <span className="flex items-center gap-1 text-[10px] font-mono text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded-full border border-emerald-800/40">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Live Running
              </span>
            </div>
            <p className="text-[11px] text-slate-400">
              {projectName || 'Autonomous multi-agent interactive application'}
            </p>
          </div>
        </div>

        {/* Viewport switcher & Tools */}
        <div className="flex items-center gap-2">
          {/* Responsive viewport selector */}
          <div className="flex items-center gap-1 bg-slate-900 p-1 rounded-xl border border-slate-800">
            <button
              onClick={() => setDevice('desktop')}
              className={`p-1.5 rounded-lg text-xs font-medium transition-all ${
                device === 'desktop' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
              }`}
              title="Desktop View (Full Width)"
            >
              <Monitor className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setDevice('tablet')}
              className={`p-1.5 rounded-lg text-xs font-medium transition-all ${
                device === 'tablet' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
              }`}
              title="Tablet View (768px)"
            >
              <Tablet className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setDevice('mobile')}
              className={`p-1.5 rounded-lg text-xs font-medium transition-all ${
                device === 'mobile' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
              }`}
              title="Mobile View (375px)"
            >
              <Smartphone className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Action buttons */}
          <button
            onClick={handleReload}
            className={`p-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 text-xs transition-all ${
              isLoading ? 'animate-spin text-cyan-400' : ''
            }`}
            title="Reload Preview Frame"
          >
            <RotateCw className="w-3.5 h-3.5" />
          </button>

          <a
            href={previewUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-cyan-950/60 hover:bg-cyan-900/60 text-cyan-300 border border-cyan-700/50 text-xs font-semibold shadow-sm transition-all"
          >
            <ExternalLink className="w-3.5 h-3.5" />
            <span>Open in Full Tab</span>
          </a>
        </div>
      </div>

      {/* Frame Container Area */}
      <div className="p-4 bg-slate-950/40 flex items-center justify-center min-h-[500px] overflow-auto">
        <div className={`transition-all duration-300 bg-white overflow-hidden ${getContainerWidth()}`}>
          <iframe
            key={reloadKey}
            title="Interactive Application Preview"
            src={previewUrl}
            className="w-full h-full border-0"
            sandbox="allow-forms allow-modals allow-popups allow-scripts allow-same-origin"
          />
        </div>
      </div>

      {/* Bottom Info Bar */}
      <div className="p-2 px-4 bg-slate-950/80 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500 font-mono">
        <span className="flex items-center gap-1.5">
          <Sparkles className="w-3 h-3 text-indigo-400" />
          Interactive sandbox powered by coder agent preview router
        </span>
        <span className="truncate max-w-xs">{previewUrl}</span>
      </div>
    </div>
  );
};
