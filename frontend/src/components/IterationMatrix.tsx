import React from 'react';
import { Repeat, XCircle, Check, Terminal, ShieldCheck, Wrench } from 'lucide-react';

interface IterationMatrixProps {
  testResults: any[];
  reviewResults: any[];
  debugResults: any[];
}

export const IterationMatrix: React.FC<IterationMatrixProps> = ({
  testResults,
  reviewResults,
  debugResults,
}) => {
  const allIterKeys = Array.from(
    new Set([
      ...testResults.map((x: any) => `${x.version}-${x.iteration}`),
      ...reviewResults.map((x: any) => `${x.version}-${x.iteration}`),
      ...debugResults.map((x: any) => `${x.version}-${x.iteration}`),
    ])
  ).sort();

  if (allIterKeys.length === 0) {
    return (
      <div className="glass-panel rounded-2xl p-12 text-center text-slate-400">
        <Repeat className="w-12 h-12 text-slate-600 mx-auto mb-3" />
        <p className="text-sm font-semibold text-slate-300">No iteration cycles recorded yet</p>
        <p className="text-xs text-slate-500 mt-1">
          When the LangGraph loop detects defects, each iteration will show test scores and automated debugger repairs here.
        </p>
      </div>
    );
  }

  return (
    <div className="glass-panel rounded-2xl border border-slate-800/80 shadow-subtle-card overflow-hidden space-y-4">
      {/* Header */}
      <div className="p-4 sm:p-5 border-b border-slate-800/80 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
            <Repeat className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-100">Self-Correcting Iteration Matrix</h2>
            <p className="text-[11px] text-slate-400">
              Iterative quality evolution: Tester ⇄ Reviewer ⇄ Debugger
            </p>
          </div>
        </div>
        <span className="text-xs font-mono px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
          {allIterKeys.length} Iteration Cycles
        </span>
      </div>

      {/* Grid of Iteration Cards */}
      <div className="p-4 sm:p-5 space-y-4">
        {allIterKeys.map((key, cardIdx) => {
          const [ver, iter] = key.split('-').map(Number);
          const tr = testResults.find((x: any) => x.version === ver && x.iteration === iter);
          const rr = reviewResults.find((x: any) => x.version === ver && x.iteration === iter);
          const dr = debugResults.find((x: any) => x.version === ver && x.iteration === iter);
          const reviewPass = rr?.status === 'PASS';
          const hasDebug = !!dr;

          return (
            <div key={key} className="relative">
              {/* Connector line between iterations */}
              {cardIdx < allIterKeys.length - 1 && (
                <div className="absolute left-6 top-full h-4 w-0.5 bg-slate-800 z-10" />
              )}

              <div
                className={`rounded-xl border p-4 sm:p-5 transition-all ${
                  reviewPass
                    ? 'border-emerald-500/30 bg-slate-900/60'
                    : 'border-purple-500/30 bg-slate-900/60'
                }`}
              >
                {/* Header of Iteration */}
                <div className="flex flex-wrap items-center justify-between gap-2 mb-4 pb-3 border-b border-slate-800/80">
                  <div className="flex items-center gap-2.5">
                    <span className="text-sm font-bold text-slate-100 font-mono">
                      v{ver} · Iteration {iter}
                    </span>
                    <span className="text-[10px] text-slate-400 bg-slate-800 px-2 py-0.5 rounded font-mono">
                      Cycle #{cardIdx + 1}
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    <span
                      className={`text-[10px] px-2.5 py-0.5 rounded-full font-medium font-mono flex items-center gap-1 ${
                        reviewPass
                          ? 'bg-emerald-950 text-emerald-300 border border-emerald-500/40'
                          : 'bg-amber-950 text-amber-300 border border-amber-500/40'
                      }`}
                    >
                      {reviewPass ? <Check className="w-3 h-3 text-emerald-400" /> : <XCircle className="w-3 h-3 text-amber-400" />}
                      {reviewPass ? 'GATE PASS' : 'REFINING'}
                    </span>
                  </div>
                </div>

                {/* Stages inside this cycle */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {/* Test Results Stage */}
                  <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800">
                    <div className="flex items-center justify-between text-xs font-semibold text-slate-300 mb-2">
                      <span className="flex items-center gap-1.5 text-sky-400">
                        <Terminal className="w-3.5 h-3.5" />
                        Sandbox Testing
                      </span>
                      {tr && (
                        <span className="font-mono text-xs font-bold text-slate-200">
                          {tr.tests_passed}/{tr.tests_total}
                        </span>
                      )}
                    </div>
                    {tr ? (
                      <div className="space-y-1.5">
                        <div className="flex justify-between text-[11px]">
                          <span className="text-slate-400">Pass Rate:</span>
                          <span className="font-mono text-emerald-400 font-semibold">
                            {tr.pass_rate ? `${tr.pass_rate.toFixed(1)}%` : '100%'}
                          </span>
                        </div>
                        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                          <div
                            className="bg-emerald-400 h-full rounded-full"
                            style={{ width: `${tr.pass_rate || (tr.tests_total ? (tr.tests_passed / tr.tests_total) * 100 : 100)}%` }}
                          />
                        </div>
                        {tr.tests_failed > 0 && (
                          <div className="text-[10px] text-rose-400 font-mono">
                            ⚠ {tr.tests_failed} failing test assertions
                          </div>
                        )}
                      </div>
                    ) : (
                      <span className="text-xs text-slate-500">Awaiting test suite execution...</span>
                    )}
                  </div>

                  {/* Review Audit Stage */}
                  <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800">
                    <div className="flex items-center justify-between text-xs font-semibold text-slate-300 mb-2">
                      <span className="flex items-center gap-1.5 text-indigo-400">
                        <ShieldCheck className="w-3.5 h-3.5" />
                        Code Review Audit
                      </span>
                      {rr && (
                        <span
                          className={`text-[10px] px-2 py-0.5 rounded font-mono font-bold ${
                            reviewPass ? 'bg-emerald-950 text-emerald-400' : 'bg-rose-950 text-rose-400'
                          }`}
                        >
                          {rr.status || (reviewPass ? 'PASS' : 'ISSUES')}
                        </span>
                      )}
                    </div>
                    {rr ? (
                      <div className="space-y-1 text-[11px]">
                        <div className="flex justify-between">
                          <span className="text-slate-400">Critical Issues:</span>
                          <span className="font-mono font-bold text-rose-400">
                            {rr.critical_issues?.length ?? 0}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Major Issues:</span>
                          <span className="font-mono text-amber-400">
                            {rr.major_issues?.length ?? 0}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Minor / Style:</span>
                          <span className="font-mono text-slate-300">
                            {rr.minor_issues?.length ?? 0}
                          </span>
                        </div>
                      </div>
                    ) : (
                      <span className="text-xs text-slate-500">Awaiting code review...</span>
                    )}
                  </div>

                  {/* Debugger Repairs Stage */}
                  <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800">
                    <div className="flex items-center justify-between text-xs font-semibold text-slate-300 mb-2">
                      <span className="flex items-center gap-1.5 text-purple-400">
                        <Wrench className="w-3.5 h-3.5" />
                        Auto Debugger
                      </span>
                      {hasDebug && (
                        <span className="text-[10px] px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800 font-mono">
                          {dr.files_modified?.length ?? 0} Files Fixed
                        </span>
                      )}
                    </div>
                    {hasDebug ? (
                      <div className="space-y-1 text-[11px]">
                        {dr.changes_summary?.slice(0, 2).map((c: string, i: number) => (
                          <div key={i} className="text-purple-300 truncate" title={c}>
                            • {c}
                          </div>
                        ))}
                        {dr.files_modified?.length > 0 && (
                          <div className="text-[10px] text-slate-400 font-mono truncate mt-1">
                            Modified: {dr.files_modified.slice(0, 2).join(', ')}
                            {dr.files_modified.length > 2 ? ` +${dr.files_modified.length - 2} more` : ''}
                          </div>
                        )}
                      </div>
                    ) : (
                      <span className="text-xs text-slate-500">
                        {reviewPass ? 'No debugging required (Pass)' : 'Awaiting debugger trigger...'}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

