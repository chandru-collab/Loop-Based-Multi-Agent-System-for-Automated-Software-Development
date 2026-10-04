import React from 'react';
import { ClipboardList, CheckCircle2, Compass, ShieldAlert, RefreshCw, FileCode, CheckSquare, Layers } from 'lucide-react';

interface OverviewSectionProps {
  requirements: any;
  plan: any;
  project: any;
  onRetry?: () => void;
}

export const OverviewSection: React.FC<OverviewSectionProps> = ({
  requirements,
  plan,
  project,
  onRetry,
}) => {
  const isFailed = project?.status === 'FAILED';

  return (
    <div className="space-y-5">
      {/* Failed Alert */}
      {isFailed && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/40 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-rose-300 font-semibold text-sm">
              <ShieldAlert className="w-4 h-4 text-rose-400" />
              <span>Workflow Execution Stopped</span>
            </div>
            <button
              onClick={onRetry}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold shadow-sm transition-all"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Retry Workflow</span>
            </button>
          </div>
          <p className="text-xs text-rose-200">
            Stage <span className="font-mono font-bold text-white">{project?.current_stage || 'Execution'}</span> encountered a failure. You can retry with fresh agent dispatch.
          </p>
        </div>
      )}

      {/* Requirements Analysis Card */}
      {requirements ? (
        <div className="glass-panel rounded-2xl border border-slate-800/80 shadow-subtle-card p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400">
                <ClipboardList className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-100">Requirements Specification</h3>
                <p className="text-[11px] text-slate-400">Deconstructed by RequirementAgent</p>
              </div>
            </div>
          </div>

          {requirements.project_summary && (
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80 text-xs text-slate-300 leading-relaxed">
              <strong className="text-sky-300 font-semibold block mb-1">Project Scope:</strong>
              {requirements.project_summary}
            </div>
          )}

          {/* Counts */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 text-center">
              <div className="text-lg font-bold text-sky-400 font-mono">
                {requirements.functional_requirements?.length ?? 0}
              </div>
              <div className="text-[11px] text-slate-400 mt-0.5">Functional Specs</div>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 text-center">
              <div className="text-lg font-bold text-emerald-400 font-mono">
                {requirements.acceptance_criteria?.length ?? 0}
              </div>
              <div className="text-[11px] text-slate-400 mt-0.5">Acceptance Criteria</div>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 text-center">
              <div className="text-lg font-bold text-amber-400 font-mono">
                {requirements.ambiguities?.length ?? 0}
              </div>
              <div className="text-[11px] text-slate-400 mt-0.5">Ambiguities Resolved</div>
            </div>
          </div>

          {/* Detailed Lists */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
            <div className="space-y-2">
              <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <CheckSquare className="w-3.5 h-3.5 text-sky-400" />
                <span>Functional Requirements</span>
              </h4>
              <ul className="space-y-1.5">
                {requirements.functional_requirements?.slice(0, 6).map((req: string, i: number) => (
                  <li key={i} className="text-xs text-slate-300 flex items-start gap-2 bg-slate-900/40 p-2 rounded-lg border border-slate-800/60">
                    <span className="text-sky-400 font-mono text-[10px] mt-0.5">#{i + 1}</span>
                    <span className="leading-relaxed">{req}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="space-y-2">
              <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>Acceptance Criteria</span>
              </h4>
              <ul className="space-y-1.5">
                {requirements.acceptance_criteria?.slice(0, 6).map((crit: string, i: number) => (
                  <li key={i} className="text-xs text-slate-300 flex items-start gap-2 bg-slate-900/40 p-2 rounded-lg border border-slate-800/60">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                    <span className="leading-relaxed">{crit}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      ) : (
        <div className="glass-panel rounded-2xl p-8 text-center text-slate-400">
          <ClipboardList className="w-10 h-10 text-slate-600 mx-auto mb-2" />
          <p className="text-sm font-semibold text-slate-300">Requirements analysis in progress...</p>
        </div>
      )}

      {/* Development Plan Card */}
      {plan && (
        <div className="glass-panel rounded-2xl border border-slate-800/80 shadow-subtle-card p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
                <Compass className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-100">System Architecture & Plan</h3>
                <p className="text-[11px] text-slate-400">Architected by PlannerAgent</p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 text-center">
              <div className="text-lg font-bold text-indigo-400 font-mono">
                {plan.modules?.length ?? 0}
              </div>
              <div className="text-[11px] text-slate-400 mt-0.5">Software Modules</div>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 text-center">
              <div className="text-lg font-bold text-purple-400 font-mono">
                {plan.api_design?.length ?? 0}
              </div>
              <div className="text-[11px] text-slate-400 mt-0.5">API Endpoints</div>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 text-center">
              <div className="text-lg font-bold text-teal-400 font-mono">
                {plan.implementation_steps?.length ?? 0}
              </div>
              <div className="text-[11px] text-slate-400 mt-0.5">Execution Milestones</div>
            </div>
          </div>

          {plan.architecture && (
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80 text-xs text-slate-300 leading-relaxed">
              <strong className="text-indigo-400 font-semibold block mb-1">Architecture Overview:</strong>
              {plan.architecture}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

