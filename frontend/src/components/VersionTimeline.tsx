import React from 'react';
import { StatusBadge } from './StatusBadge';
import { History, MessageSquare, GitCommit } from 'lucide-react';

interface VersionTimelineProps {
  versions: any[];
  evaluations: any[];
}

export const VersionTimeline: React.FC<VersionTimelineProps> = ({ versions, evaluations }) => {
  if (!versions || versions.length === 0) {
    return (
      <div className="glass-panel rounded-2xl p-12 text-center text-slate-400">
        <History className="w-12 h-12 text-slate-600 mx-auto mb-3" />
        <p className="text-sm font-semibold text-slate-300">No version checkpoints logged yet</p>
        <p className="text-xs text-slate-500 mt-1">
          Every autonomous build iteration or user-requested revision creates an immutable version snapshot.
        </p>
      </div>
    );
  }

  return (
    <div className="glass-panel rounded-2xl border border-slate-800/80 shadow-subtle-card overflow-hidden space-y-4">
      <div className="p-4 sm:p-5 border-b border-slate-800/80 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
            <History className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-100">Release Version History</h2>
            <p className="text-[11px] text-slate-400">Evolution of software iterations across revisions</p>
          </div>
        </div>
        <span className="text-xs font-mono px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
          {versions.length} Total Versions
        </span>
      </div>

      <div className="p-4 sm:p-5 space-y-3">
        {versions.map((v: any) => {
          const ev = evaluations?.find((e: any) => e.version === v.version);

          return (
            <div
              key={v.version}
              className="p-3.5 rounded-xl border border-slate-800/80 bg-slate-900/40 hover:border-slate-700 space-y-3 transition-all"
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-md bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center font-bold font-mono text-indigo-300 text-xs">
                    v{v.version}
                  </div>
                  <StatusBadge status={v.status} size="sm" />
                  {v.approval_status && <StatusBadge status={v.approval_status} size="sm" />}
                  {v.evaluation_status && (
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded-full font-mono font-medium ${
                        v.evaluation_status === 'PASS'
                          ? 'bg-emerald-950/70 text-emerald-300 border border-emerald-500/30'
                          : 'bg-rose-950/70 text-rose-300 border border-rose-500/30'
                      }`}
                    >
                      Eval: {v.evaluation_status}
                    </span>
                  )}
                </div>

                {v.created_at && (
                  <span className="text-[10px] font-mono text-slate-500">
                    {new Date(v.created_at).toLocaleString()}
                  </span>
                )}
              </div>

              {/* Evaluation score summary */}
              {ev && (
                <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 text-xs">
                  <div className="bg-slate-950/60 p-2 rounded-lg border border-slate-800">
                    <span className="text-slate-500 block text-[10px]">Requirements:</span>
                    <span className="font-mono font-semibold text-slate-200">{ev.requirements_total ?? '—'}</span>
                  </div>
                  <div className="bg-slate-950/60 p-2 rounded-lg border border-slate-800">
                    <span className="text-slate-500 block text-[10px]">Tests Executed:</span>
                    <span className="font-mono font-semibold text-slate-200">{ev.tests_total ?? '—'}</span>
                  </div>
                  <div className="bg-slate-950/60 p-2 rounded-lg border border-slate-800">
                    <span className="text-slate-500 block text-[10px]">Pass Rate:</span>
                    <span className="font-mono font-semibold text-emerald-400">
                      {ev.test_pass_rate != null ? `${ev.test_pass_rate.toFixed(1)}%` : '—'}
                    </span>
                  </div>
                  <div className="bg-slate-950/60 p-2 rounded-lg border border-slate-800">
                    <span className="text-slate-500 block text-[10px]">Iterations:</span>
                    <span className="font-mono font-semibold text-purple-300">{ev.iterations_used ?? '—'}</span>
                  </div>
                  <div className="bg-slate-950/60 p-2 rounded-lg border border-slate-800">
                    <span className="text-slate-500 block text-[10px]">Req Coverage:</span>
                    <span className="font-mono font-semibold text-sky-300">
                      {ev.requirements_coverage != null ? `${ev.requirements_coverage.toFixed(1)}%` : '—'}
                    </span>
                  </div>
                </div>
              )}

              {/* Revision feedback note */}
              {v.revision_feedback && (
                <div className="p-2.5 rounded-lg bg-amber-950/20 border border-amber-500/30 text-xs text-amber-200 flex items-start gap-2">
                  <MessageSquare className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-semibold text-amber-300">Revision Prompt:</span> "{v.revision_feedback}"
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

