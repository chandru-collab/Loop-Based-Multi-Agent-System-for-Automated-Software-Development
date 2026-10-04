import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Bot, Sparkles, Terminal, Clock, CheckCircle2, AlertCircle } from 'lucide-react';

interface AgentExecutionViewProps {
  agentRuns: any[];
  requirements: any;
  plan: any;
  testResults: any[];
  reviewResults: any[];
  debugResults: any[];
  evaluation: any;
  documentation: any;
}

export const AgentExecutionView: React.FC<AgentExecutionViewProps> = ({
  agentRuns,
  requirements,
  plan,
  testResults,
  reviewResults,
  debugResults,
  evaluation,
  documentation,
}) => {
  const [expanded, setExpanded] = useState<string | null>(null);

  if (!agentRuns || agentRuns.length === 0) {
    return (
      <div className="glass-panel rounded-2xl p-12 text-center text-slate-400">
        <Bot className="w-12 h-12 text-slate-600 mx-auto mb-3" />
        <p className="text-sm font-semibold text-slate-300">No agent execution runs recorded yet</p>
        <p className="text-xs text-slate-500 mt-1">Start the project workflow to observe LangGraph agent step dispatches.</p>
      </div>
    );
  }

  const getExplainability = (agent: any): Record<string, any> => {
    const name = agent.agent_name;
    if (name === 'RequirementAgent' && requirements) {
      return {
        'Functional Requirements': requirements.functional_requirements?.length ?? 0,
        'Ambiguities Detected': requirements.ambiguities?.length ?? 0,
        'Acceptance Criteria': requirements.acceptance_criteria?.length ?? 0,
        'Non-functional Specs': requirements.non_functional_requirements?.length ?? 0,
      };
    }
    if (name === 'PlannerAgent' && plan) {
      return {
        'Modules Planned': plan.modules?.length ?? 0,
        'API Endpoints': plan.api_design?.length ?? 0,
        'Database Entities': plan.database_design?.entities?.length ?? plan.database_design?.length ?? 0,
        'Implementation Milestones': plan.implementation_steps?.length ?? 0,
      };
    }
    if (name === 'TestingAgent' && testResults?.length > 0) {
      const last = testResults[testResults.length - 1];
      return {
        'Tests Executed': last.tests_total ?? 0,
        'Passed': last.tests_passed ?? 0,
        'Failed': last.tests_failed ?? 0,
        'Pass Rate': last.pass_rate ? `${last.pass_rate.toFixed(1)}%` : 'N/A',
      };
    }
    if (name === 'ReviewerAgent' && reviewResults?.length > 0) {
      const last = reviewResults[reviewResults.length - 1];
      return {
        'Critical Issues': last.critical_issues?.length ?? 0,
        'Major Issues': last.major_issues?.length ?? 0,
        'Minor Issues': last.minor_issues?.length ?? 0,
        'Security Issues': last.security_issues?.length ?? 0,
      };
    }
    if (name === 'DebuggerAgent' && debugResults?.length > 0) {
      const last = debugResults[debugResults.length - 1];
      return {
        'Files Patched': last.files_modified?.length ?? 0,
        'Issues Addressed': last.issues_addressed?.length ?? 0,
      };
    }
    if (name === 'EvaluationMetricsAgent' && evaluation) {
      return {
        'Requirements Coverage': `${evaluation.requirements_coverage?.toFixed(1) ?? 0}%`,
        'Test Pass Rate': `${evaluation.test_pass_rate?.toFixed(1) ?? 0}%`,
        'Blocking Issues': evaluation.review_critical_issues ?? 0,
        'Quality Gate Decision': evaluation.final_quality_status ?? 'N/A',
      };
    }
    if (name === 'DocumentationAgent' && documentation) {
      return {
        'Documentation Files Created': documentation.files_created?.length ?? 0,
        'Files Updated': documentation.files_updated?.length ?? 0,
      };
    }
    return {};
  };

  return (
    <div className="glass-panel rounded-2xl border border-slate-800/80 shadow-subtle-card overflow-hidden space-y-4">
      {/* Header */}
      <div className="p-4 sm:p-5 border-b border-slate-800/80 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-100">Agent Execution & Trace Inspector</h2>
            <p className="text-[11px] text-slate-400">Audit trail of autonomous agent deliberations and actions</p>
          </div>
        </div>
        <span className="text-xs font-mono px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
          {agentRuns.length} Agent Executions
        </span>
      </div>

      {/* List */}
      <div className="p-4 sm:p-5 space-y-2.5">
        {agentRuns.map((run: any) => {
          const key = run.id || run.agent_name;
          const isOpen = expanded === key;
          const dur =
            run.duration_seconds != null
              ? `${run.duration_seconds.toFixed(1)}s`
              : run.completed_at && run.started_at
              ? `${((new Date(run.completed_at).getTime() - new Date(run.started_at).getTime()) / 1000).toFixed(1)}s`
              : '—';
          const explain = getExplainability(run);
          const isSuccess = run.status === 'completed';
          const isFailed = run.status === 'failed';

          return (
            <div
              key={key}
              className={`rounded-xl border transition-all overflow-hidden ${
                isOpen
                  ? 'border-indigo-500/50 bg-slate-900/90'
                  : 'border-slate-800/80 bg-slate-900/40 hover:border-slate-700'
              }`}
            >
              <button
                onClick={() => setExpanded(isOpen ? null : key)}
                className="w-full flex items-center justify-between p-3 sm:p-3.5 text-left gap-3"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div
                    className={`w-2 h-2 rounded-full shrink-0 ${
                      isSuccess ? 'bg-emerald-400' : isFailed ? 'bg-rose-400' : 'bg-slate-500'
                    }`}
                  />
                  <div className="min-w-0">
                    <span className="font-semibold text-xs text-slate-200 block truncate">
                      {run.agent_name}
                    </span>
                    <span className="text-[10px] text-slate-500 font-mono">
                      {run.started_at ? new Date(run.started_at).toLocaleTimeString() : 'Queued'}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <span className="text-[11px] font-mono text-slate-400 bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700">
                    ⏱ {dur}
                  </span>
                  <span
                    className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
                      isSuccess
                        ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-500/40'
                        : isFailed
                        ? 'bg-rose-950/80 text-rose-300 border border-rose-500/40'
                        : 'bg-slate-800 text-slate-400'
                    }`}
                  >
                    {run.status}
                  </span>
                  {isOpen ? (
                    <ChevronUp className="w-4 h-4 text-slate-400" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-slate-400" />
                  )}
                </div>
              </button>

              {isOpen && (
                <div className="p-4 bg-slate-950/70 border-t border-slate-800 space-y-3">
                  {/* Summary & Timestamps */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                    {run.started_at && (
                      <div className="bg-slate-900/80 p-2 rounded-lg border border-slate-800">
                        <span className="text-slate-400 block text-[10px]">Started:</span>
                        <span className="text-slate-200 font-mono text-[11px]">{new Date(run.started_at).toLocaleString()}</span>
                      </div>
                    )}
                    {run.completed_at && (
                      <div className="bg-slate-900/80 p-2 rounded-lg border border-slate-800">
                        <span className="text-slate-400 block text-[10px]">Completed:</span>
                        <span className="text-slate-200 font-mono text-[11px]">{new Date(run.completed_at).toLocaleString()}</span>
                      </div>
                    )}

                    {run.input_summary && (
                      <div className="sm:col-span-2 bg-slate-900/80 p-3 rounded-lg border border-slate-800">
                        <span className="text-indigo-400 font-semibold block text-[10px] uppercase tracking-wider mb-1">
                          Input Intent:
                        </span>
                        <p className="text-slate-300 text-xs leading-relaxed">{run.input_summary}</p>
                      </div>
                    )}

                    {run.output_summary && (
                      <div className="sm:col-span-2 bg-slate-900/80 p-3 rounded-lg border border-slate-800">
                        <span className="text-sky-400 font-semibold block text-[10px] uppercase tracking-wider mb-1">
                          Output Synthesis:
                        </span>
                        <p className="text-slate-300 text-xs leading-relaxed">{run.output_summary}</p>
                      </div>
                    )}

                    {run.error_message && (
                      <div className="sm:col-span-2 bg-rose-950/60 p-3 rounded-lg border border-rose-500/50 text-rose-300">
                        <span className="font-semibold block text-[10px] uppercase tracking-wider mb-1 text-rose-400">
                          Error Diagnostic:
                        </span>
                        <p className="font-mono text-xs">{run.error_message}</p>
                      </div>
                    )}
                  </div>

                  {/* Explainability Matrix */}
                  {Object.keys(explain).length > 0 && (
                    <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800 space-y-2">
                      <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-indigo-300">
                        <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                        Agent Decision Metrics
                      </div>
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                        {Object.entries(explain).map(([label, val]) => (
                          <div key={label} className="bg-slate-950/60 p-2 rounded-lg border border-slate-800 text-center">
                            <div className="text-sm font-bold text-sky-400 font-mono">{String(val)}</div>
                            <div className="text-[10px] text-slate-400 mt-0.5">{label}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

