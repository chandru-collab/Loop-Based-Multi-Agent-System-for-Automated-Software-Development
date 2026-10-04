import React, { useState } from 'react';
import { X, Sparkles, Wand2, Layers, Play } from 'lucide-react';

interface CreateProjectModalProps {
  onClose: () => void;
  onCreate: (data: {
    name: string;
    description: string;
    max_iterations: number;
    experiment_type: string;
  }) => Promise<void>;
}

const TEMPLATES = [
  {
    name: 'Interactive Chess Game App',
    description: 'Build a responsive Chess Game with complete move validation, board UI, turn-based mechanics, move history log, and unit test suite.',
    iterations: 4,
    experiment: 'B',
  },
  {
    name: 'Todo REST API with Filtering & Auth',
    description: 'Build a clean Todo REST API with CRUD operations, status filtering, pagination, request validation, error handlers, and Pytest suites.',
    iterations: 3,
    experiment: 'B',
  },
  {
    name: 'Crypto & Stock Price Tracker',
    description: 'Create a financial dashboard app with live simulated ticker data, portfolio tracking, alert triggers, and interactive chart visualizations.',
    iterations: 4,
    experiment: 'B',
  },
  {
    name: 'Markdown Note Taking App with Tags',
    description: 'Build a full-featured markdown notes application with search, categorized tags, live editor preview, and local storage persistence.',
    iterations: 3,
    experiment: 'B',
  },
];

export const CreateProjectModal: React.FC<CreateProjectModalProps> = ({ onClose, onCreate }) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [maxIterations, setMaxIterations] = useState(5);
  const [experimentType, setExperimentType] = useState('B');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !description.trim()) return;
    setLoading(true);
    try {
      await onCreate({
        name,
        description,
        max_iterations: maxIterations,
        experiment_type: experimentType,
      });
    } finally {
      setLoading(false);
    }
  };

  const loadTemplate = (tmpl: typeof TEMPLATES[0]) => {
    setName(tmpl.name);
    setDescription(tmpl.description);
    setMaxIterations(tmpl.iterations);
    setExperimentType(tmpl.experiment);
  };

  return (
    <div className="fixed inset-0 bg-black/75 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-in fade-in duration-150">
      <div className="glass-panel w-full max-w-xl rounded-2xl border border-slate-700/80 shadow-elevated overflow-hidden">
        {/* Header */}
        <div className="p-4 px-6 border-b border-slate-800/80 flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <Layers className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-slate-100">Create New Autonomous Project</h2>
              <p className="text-[11px] text-slate-400">
                Specify requirements in natural English — LangGraph orchestrates the rest
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-all"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          {/* Quick Preset Badges */}
          <div className="space-y-1.5">
            <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-sky-400" />
              Quick Project Starters:
            </span>
            <div className="flex flex-wrap gap-1.5">
              {TEMPLATES.map((tmpl) => (
                <button
                  key={tmpl.name}
                  type="button"
                  onClick={() => loadTemplate(tmpl)}
                  className="text-xs px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 hover:border-slate-700 transition-all"
                >
                  {tmpl.name}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
              Project Name
            </label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:border-indigo-500 outline-none transition-all"
              placeholder="E.g., Chess Web Application"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
              Natural Language Software Requirement
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
              rows={3}
              className="w-full bg-slate-900 border border-slate-800 rounded-lg p-3 text-xs text-slate-100 placeholder-slate-500 focus:border-indigo-500 outline-none transition-all leading-relaxed"
              placeholder="Describe what features, API endpoints, logic, and test criteria your application needs..."
            />
          </div>

          {/* Configuration Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                Max Dev Iterations (Loop Limit)
              </label>
              <div className="flex items-center gap-2.5">
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={maxIterations}
                  onChange={(e) => setMaxIterations(Number(e.target.value))}
                  className="flex-1 accent-indigo-500 cursor-pointer"
                />
                <span className="w-8 font-mono font-bold text-center bg-slate-900 border border-slate-800 py-0.5 rounded text-xs text-sky-300">
                  {maxIterations}
                </span>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                Workflow Orchestration Mode
              </label>
              <div className="grid grid-cols-2 gap-1.5">
                <button
                  type="button"
                  onClick={() => setExperimentType('B')}
                  className={`p-1.5 rounded-lg text-left border text-xs transition-all ${
                    experimentType === 'B'
                      ? 'border-indigo-500 bg-indigo-950/50 text-indigo-200'
                      : 'border-slate-800 bg-slate-900/60 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  <div className="font-semibold text-xs">Exp B (Loop)</div>
                  <div className="text-[10px] text-slate-400">Self-Correcting</div>
                </button>

                <button
                  type="button"
                  onClick={() => setExperimentType('A')}
                  className={`p-1.5 rounded-lg text-left border text-xs transition-all ${
                    experimentType === 'A'
                      ? 'border-indigo-500 bg-indigo-950/50 text-indigo-200'
                      : 'border-slate-800 bg-slate-900/60 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  <div className="font-semibold text-xs">Exp A (Single)</div>
                  <div className="text-[10px] text-slate-400">Single-Pass</div>
                </button>
              </div>
            </div>
          </div>

          {/* Action Footer */}
          <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-slate-800/80">
            <button
              type="button"
              onClick={onClose}
              className="px-3.5 py-1.5 rounded-lg border border-slate-800 text-slate-300 hover:bg-slate-800 text-xs transition-all"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !name.trim() || !description.trim()}
              className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs shadow-sm active:scale-[0.98] transition-all disabled:opacity-50"
            >
              <Play className="w-3.5 h-3.5" />
              <span>{loading ? 'Initializing...' : 'Create & Launch'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

