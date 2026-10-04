import React from 'react';
import { Bot, Plus, Activity, Layers, Sparkles } from 'lucide-react';

interface NavbarProps {
  onNewProject: () => void;
  projectCount?: number;
  activeProject?: any;
}

export const Navbar: React.FC<NavbarProps> = ({ onNewProject, projectCount = 0, activeProject }) => {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-[#070a13]/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between gap-4">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white shadow-sm ring-1 ring-white/20">
            <Layers className="w-4 h-4" />
          </div>

          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm sm:text-base font-bold text-slate-100 tracking-tight">
                LangGraph Studio
              </h1>
              <span className="hidden sm:inline-block text-[10px] font-mono px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 border border-slate-700">
                v2.0 · Multi-Agent Loop
              </span>
            </div>
          </div>
        </div>

        {/* Action Controls & Active Context */}
        <div className="flex items-center gap-3">
          {activeProject ? (
            <div className="hidden md:flex items-center gap-2 bg-slate-900 border border-slate-800 px-3 py-1 rounded-lg text-xs">
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
              <span className="text-slate-400">Project:</span>
              <span className="font-semibold text-slate-200 max-w-[150px] truncate">
                {activeProject.name}
              </span>
            </div>
          ) : (
            <div className="hidden sm:flex items-center gap-1.5 text-xs text-slate-400 font-mono">
              <Activity className="w-3.5 h-3.5 text-emerald-400" />
              <span>{projectCount} projects loaded</span>
            </div>
          )}

          <button
            onClick={onNewProject}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs shadow-sm active:scale-[0.98] transition-all"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>New Project</span>
          </button>
        </div>
      </div>
    </header>
  );
};

