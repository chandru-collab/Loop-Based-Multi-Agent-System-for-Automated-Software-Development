import React, { useState } from 'react';
import { api } from '../services/api';
import confetti from 'canvas-confetti';
import { CheckCircle2, RefreshCw, Send, AlertCircle, Sparkles, FileCode, CheckCheck, ShieldAlert, Cpu } from 'lucide-react';

interface ApprovalStationProps {
  projectId: string;
  project: any;
  evaluation: any;
  documentation: any;
  requirements: any;
  testResults: any[];
  reviewResults: any[];
  onAction: () => void;
}

export const ApprovalStation: React.FC<ApprovalStationProps> = ({
  projectId,
  project,
  evaluation,
  documentation,
  requirements,
  testResults,
  reviewResults,
  onAction,
}) => {
  const [revisionMode, setRevisionMode] = useState(false);
  const [feedback, setFeedback] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const revisionsUsed = project?.revision_count ?? 0;
  const maxRevisions = project?.max_revisions ?? 3;

  const handleApprove = async () => {
    setLoading(true);
    setError('');
    try {
      confetti({
        particleCount: 70,
        spread: 60,
        origin: { y: 0.6 },
        colors: ['#6366f1', '#38bdf8', '#10b981', '#f59e0b'],
      });

      await api.approveProject(projectId);
      onAction();
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Approval failed');
    } finally {
      setLoading(false);
    }
  };

  const handleRevise = async () => {
    if (!feedback.trim()) {
      setError('Feedback description is required');
      return;
    }
    setLoading(true);
    setError('');
    try {
      await api.reviseProject(projectId, feedback);
      onAction();
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Revision failed');
    } finally {
      setLoading(false);
    }
  };

  const lastTest = testResults?.[testResults.length - 1];
  const lastReview = reviewResults?.[reviewResults.length - 1];

  const quickFeedbackSuggestions = [
    'Add more unit tests for edge cases and validation failures',
    'Enhance error handling and return clean JSON error responses',
    'Refactor project files into distinct service and repository layers',
    'Improve documentation and add comprehensive API usage examples',
  ];

  const summaryStats = [
    { label: 'Current Version', value: `v${project?.current_version ?? 1}`, icon: <Cpu className="w-3.5 h-3.5 text-sky-400" /> },
    { label: 'Requirements', value: requirements?.functional_requirements?.length ?? 0, icon: <CheckCheck className="w-3.5 h-3.5 text-indigo-400" /> },
    { label: 'Tests Passed', value: `${lastTest?.tests_passed ?? 0}/${lastTest?.tests_total ?? 0}`, icon: <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> },
    { label: 'Critical Issues', value: lastReview?.critical_issues?.length ?? 0, icon: <ShieldAlert className="w-3.5 h-3.5 text-rose-400" /> },
    { label: 'Quality Gate', value: evaluation?.final_quality_status ?? 'PASS', icon: <Sparkles className="w-3.5 h-3.5 text-amber-400" /> },
    { label: 'Doc Files', value: documentation?.files_created?.length ?? 0, icon: <FileCode className="w-3.5 h-3.5 text-purple-400" /> },
  ];

  return (
    <div className="glass-panel rounded-2xl border border-amber-500/40 bg-amber-950/20 p-5 shadow-subtle-card space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-300">
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm sm:text-base font-bold text-amber-200">
                User Approval & Release Gate
              </h2>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30">
                Action Required
              </span>
            </div>
            <p className="text-xs text-slate-300 mt-0.5">
              LangGraph has completed stage execution. Inspect quality metrics below to approve or request an autonomous revision.
            </p>
          </div>
        </div>

        {/* Revision meter */}
        <div className="bg-slate-900/80 px-3 py-1.5 rounded-lg border border-slate-800 flex items-center gap-2 text-xs text-slate-300 self-start sm:self-auto">
          <span className="text-slate-400">Revisions:</span>
          <span className="font-bold text-amber-400 font-mono">
            {revisionsUsed} / {maxRevisions}
          </span>
          {revisionsUsed >= maxRevisions && (
            <span className="text-[10px] text-rose-400 font-medium">(Max reached)</span>
          )}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
        {summaryStats.map((item) => (
          <div
            key={item.label}
            className="p-2.5 rounded-xl border border-slate-800 bg-slate-900/60 flex flex-col justify-between"
          >
            <div className="flex items-center justify-between mb-1">
              <span className="text-[10px] text-slate-400">{item.label}</span>
              {item.icon}
            </div>
            <div className="text-base font-bold text-slate-100 font-mono tracking-tight">{item.value}</div>
          </div>
        ))}
      </div>

      {/* Quality Summary Banner */}
      {evaluation?.quality_summary && (
        <div className="p-3 rounded-xl border border-slate-800 bg-slate-900/60 text-xs text-slate-300 flex items-start gap-2">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400 shrink-0 mt-0.5" />
          <div>
            <strong className="text-slate-200 font-semibold">Quality Assessment:</strong>{' '}
            {evaluation.quality_summary}
          </div>
        </div>
      )}

      {error && (
        <div className="p-2.5 rounded-xl bg-rose-950/60 border border-rose-500/50 text-xs text-rose-300 flex items-center gap-2">
          <AlertCircle className="w-3.5 h-3.5 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Action Buttons / Revision Form */}
      {!revisionMode ? (
        <div className="flex flex-wrap gap-2.5 pt-2 border-t border-slate-800/80">
          <button
            onClick={handleApprove}
            disabled={loading}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-sm active:scale-[0.98] transition-all disabled:opacity-50"
          >
            {loading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <CheckCircle2 className="w-3.5 h-3.5" />}
            <span>Approve & Package Release ZIP</span>
          </button>

          <button
            onClick={() => setRevisionMode(true)}
            disabled={loading || revisionsUsed >= maxRevisions}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700 text-xs font-semibold active:scale-[0.98] transition-all disabled:opacity-50"
          >
            <RefreshCw className="w-3.5 h-3.5 text-amber-400" />
            <span>Request Revision Loop</span>
          </button>
        </div>
      ) : (
        <div className="space-y-2.5 pt-2 border-t border-slate-800/80">
          <div className="flex items-center justify-between">
            <label className="text-xs font-semibold text-slate-200 flex items-center gap-1.5">
              <RefreshCw className="w-3 h-3 text-amber-400" />
              Provide Revision Feedback for Next Agent Iteration:
            </label>
            <span className="text-[10px] text-slate-400">LangGraph will re-route with this feedback</span>
          </div>

          <textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="E.g., Please improve test coverage on the pagination helper and add request schema validation..."
            className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-slate-100 placeholder-slate-500 h-24 focus:border-amber-400 outline-none transition-all leading-relaxed"
          />

          {/* Quick feedback chips */}
          <div className="space-y-1">
            <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">
              Quick Suggestions:
            </span>
            <div className="flex flex-wrap gap-1">
              {quickFeedbackSuggestions.map((suggestion, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => setFeedback((prev) => (prev ? `${prev}. ${suggestion}` : suggestion))}
                  className="text-[10px] bg-slate-900 hover:bg-slate-800 text-slate-300 px-2 py-0.5 rounded-md border border-slate-800 transition-all text-left"
                >
                  + {suggestion}
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-2 pt-1">
            <button
              onClick={handleRevise}
              disabled={loading || !feedback.trim()}
              className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold shadow-sm active:scale-[0.98] transition-all disabled:opacity-50"
            >
              {loading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
              <span>Submit Revision Request</span>
            </button>
            <button
              onClick={() => {
                setRevisionMode(false);
                setFeedback('');
                setError('');
              }}
              className="px-3 py-1.5 rounded-lg border border-slate-800 text-slate-300 hover:bg-slate-800 text-xs transition-all"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

