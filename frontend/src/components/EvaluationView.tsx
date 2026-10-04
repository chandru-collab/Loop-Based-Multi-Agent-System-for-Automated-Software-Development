import React from 'react';
import { BarChart3, CheckCircle2, AlertTriangle, Lightbulb, ShieldAlert, Cpu, Sparkles, Award } from 'lucide-react';

interface EvaluationViewProps {
  evaluation: any;
}

export const EvaluationView: React.FC<EvaluationViewProps> = ({ evaluation }) => {
  if (!evaluation) {
    return (
      <div className="glass-panel rounded-2xl p-12 text-center text-slate-400">
        <BarChart3 className="w-12 h-12 text-slate-600 mx-auto mb-3" />
        <p className="text-sm font-semibold text-slate-300">Evaluation not yet computed</p>
        <p className="text-xs text-slate-500 mt-1">
          The Evaluation Agent analyzes test coverage, requirement satisfaction, and review findings when the build finishes.
        </p>
      </div>
    );
  }

  const isPass = evaluation.final_quality_status === 'PASS';

  const scoreSections = [
    {
      title: 'Requirements Scope',
      icon: <CheckCircle2 className="w-3.5 h-3.5 text-sky-400" />,
      items: [
        { label: 'Total Requirements', val: evaluation.requirements_total ?? '—' },
        { label: 'Satisfied Count', val: evaluation.requirements_satisfied ?? '—' },
        { label: 'Coverage Score', val: evaluation.requirements_coverage != null ? `${evaluation.requirements_coverage.toFixed(1)}%` : '—', highlight: true },
      ],
    },
    {
      title: 'Acceptance Criteria',
      icon: <Award className="w-3.5 h-3.5 text-indigo-400" />,
      items: [
        { label: 'Total Criteria', val: evaluation.acceptance_criteria_total ?? '—' },
        { label: 'Satisfied Count', val: evaluation.acceptance_criteria_satisfied ?? '—' },
        { label: 'Criteria Coverage', val: evaluation.acceptance_criteria_coverage != null ? `${evaluation.acceptance_criteria_coverage.toFixed(1)}%` : '—', highlight: true },
      ],
    },
    {
      title: 'Sandbox Testing',
      icon: <Cpu className="w-3.5 h-3.5 text-emerald-400" />,
      items: [
        { label: 'Tests Executed', val: evaluation.tests_total ?? '—' },
        { label: 'Passed / Failed', val: `${evaluation.tests_passed ?? 0} / ${evaluation.tests_failed ?? 0}` },
        { label: 'Test Pass Rate', val: evaluation.test_pass_rate != null ? `${evaluation.test_pass_rate.toFixed(1)}%` : '—', highlight: true },
      ],
    },
    {
      title: 'Review Audit',
      icon: <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />,
      items: [
        { label: 'Critical Blockers', val: evaluation.review_critical_issues ?? 0 },
        { label: 'Major Issues', val: evaluation.review_major_issues ?? 0 },
        { label: 'Minor / Style', val: evaluation.review_minor_issues ?? 0 },
      ],
    },
    {
      title: 'Security Posture',
      icon: <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />,
      items: [
        { label: 'Security Issues', val: evaluation.security_issue_count ?? 0 },
        { label: 'Security Gate', val: (evaluation.security_issue_count ?? 0) === 0 ? 'CLEAN' : 'FLAGGED', highlight: true },
      ],
    },
    {
      title: 'Development Metrics',
      icon: <Sparkles className="w-3.5 h-3.5 text-purple-400" />,
      items: [
        { label: 'Iterations Used', val: evaluation.iterations_used ?? '—' },
        { label: 'Files Generated', val: evaluation.files_generated ?? '—' },
        { label: 'Files Modified', val: evaluation.files_modified ?? '—' },
      ],
    },
  ];

  return (
    <div className="glass-panel rounded-2xl border border-slate-800/80 shadow-subtle-card overflow-hidden space-y-4 p-5">
      {/* Header with Quality Gate Decision */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-800/80">
        <div>
          <h2 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-indigo-400" />
            Quality Gate Assessment
          </h2>
          <p className="text-[11px] text-slate-400">
            Multi-dimensional evaluation computed by EvaluationMetricsAgent
          </p>
        </div>

        <div
          className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-semibold font-mono ${
            isPass
              ? 'bg-emerald-950/70 text-emerald-300 border-emerald-500/30'
              : 'bg-rose-950/70 text-rose-300 border-rose-500/30'
          }`}
        >
          {isPass ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> : <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />}
          <span>Decision: {evaluation.final_quality_status ?? '—'}</span>
        </div>
      </div>

      {/* Scorecards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {scoreSections.map((sec) => (
          <div
            key={sec.title}
            className="p-3.5 rounded-xl border border-slate-800/80 bg-slate-900/60 space-y-2.5 transition-all hover:border-slate-700"
          >
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-300">
              {sec.icon}
              <span>{sec.title}</span>
            </div>

            <div className="space-y-1.5">
              {sec.items.map((item) => (
                <div key={item.label} className="flex justify-between text-xs">
                  <span className="text-slate-400">{item.label}</span>
                  <span
                    className={`font-mono ${
                      item.highlight ? 'text-sky-300 font-semibold' : 'text-slate-200'
                    }`}
                  >
                    {String(item.val)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Quality Summary Quote */}
      {evaluation.quality_summary && (
        <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80 text-xs text-slate-300 leading-relaxed">
          <strong className="text-indigo-400 font-semibold block mb-1">Executive Summary:</strong>
          {evaluation.quality_summary}
        </div>
      )}

      {/* Risks & Recommendations */}
      {(evaluation.risks?.length > 0 || evaluation.recommendations?.length > 0) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {evaluation.risks?.length > 0 && (
            <div className="p-3.5 rounded-xl bg-amber-950/20 border border-amber-500/30 space-y-2">
              <div className="flex items-center gap-2 text-xs font-semibold text-amber-300 uppercase tracking-wider">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                <span>Identified Risks ({evaluation.risks.length})</span>
              </div>
              <ul className="space-y-1 text-xs text-amber-200/90">
                {evaluation.risks.map((r: string, i: number) => (
                  <li key={i} className="flex items-start gap-1.5">
                    <span className="text-amber-400">•</span>
                    <span>{r}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {evaluation.recommendations?.length > 0 && (
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
              <div className="flex items-center gap-2 text-xs font-semibold text-indigo-300 uppercase tracking-wider">
                <Lightbulb className="w-3.5 h-3.5 text-indigo-400" />
                <span>Recommendations ({evaluation.recommendations.length})</span>
              </div>
              <ul className="space-y-1 text-xs text-slate-300">
                {evaluation.recommendations.slice(0, 4).map((rec: string, i: number) => (
                  <li key={i} className="flex items-start gap-1.5">
                    <span className="text-indigo-400">•</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

