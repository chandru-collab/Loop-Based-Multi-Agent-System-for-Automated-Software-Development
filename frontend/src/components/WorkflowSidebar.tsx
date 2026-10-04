import React from 'react';
import { WORKFLOW_STAGES, getStageStatus } from '../utils/workflowUtils';
import {
  Check,
  X,
  RefreshCw,
  Clock,
  ChevronRight,
  Repeat,
  Workflow,
  Bot,
  Terminal,
  Sparkles,
  ShieldCheck,
  GitCommit,
  PackageCheck,
  MonitorPlay,
  Code2
} from 'lucide-react';

interface WorkflowSidebarProps {
  project: any;
  agentRuns: any[];
  activeTab?: string;
  onNavigateTab?: (tab: string) => void;
}

export const WorkflowSidebar: React.FC<WorkflowSidebarProps> = ({
  project,
  agentRuns,
  onNavigateTab,
}) => {
  const getStageIcon = (key: string) => {
    switch (key) {
      case 'requirement':
        return <Bot className="w-3.5 h-3.5" />;
      case 'planner':
        return <Workflow className="w-3.5 h-3.5" />;
      case 'coder':
        return <Terminal className="w-3.5 h-3.5" />;
      case 'tester':
        return <Sparkles className="w-3.5 h-3.5" />;
      case 'reviewer':
        return <ShieldCheck className="w-3.5 h-3.5" />;
      case 'debugger':
        return <Repeat className="w-3.5 h-3.5" />;
      case 'evaluator':
        return <GitCommit className="w-3.5 h-3.5" />;
      case 'documentor':
        return <Terminal className="w-3.5 h-3.5" />;
      case 'approval':
        return <Clock className="w-3.5 h-3.5" />;
      case 'packaging':
        return <PackageCheck className="w-3.5 h-3.5" />;
      default:
        return <Bot className="w-3.5 h-3.5" />;
    }
  };

  const getStageStyles = (status: string) => {
    switch (status) {
      case 'RUNNING':
        return {
          card: 'bg-sky-950/60 border-sky-500/40 text-sky-200',
          iconBg: 'bg-sky-500/20 text-sky-300 border-sky-400/30',
          text: 'text-sky-200 font-semibold',
          badge: <RefreshCw className="w-3.5 h-3.5 text-sky-400 animate-spin" />,
        };
      case 'COMPLETED':
        return {
          card: 'bg-slate-900/60 border-slate-800 hover:border-slate-700',
          iconBg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
          text: 'text-slate-200',
          badge: <Check className="w-3.5 h-3.5 text-emerald-400" />,
        };
      case 'WAITING':
        return {
          card: 'bg-amber-950/50 border-amber-500/40',
          iconBg: 'bg-amber-500/20 text-amber-300 border-amber-400/30',
          text: 'text-amber-200 font-semibold',
          badge: <Clock className="w-3.5 h-3.5 text-amber-400" />,
        };
      case 'FAILED':
        return {
          card: 'bg-rose-950/50 border-rose-500/40',
          iconBg: 'bg-rose-500/20 text-rose-300 border-rose-400/30',
          text: 'text-rose-200 font-semibold',
          badge: <X className="w-3.5 h-3.5 text-rose-400" />,
        };
      default:
        return {
          card: 'bg-slate-900/30 border-slate-800/60 hover:border-slate-800 opacity-60',
          iconBg: 'bg-slate-800 text-slate-400 border-slate-700',
          text: 'text-slate-400',
          badge: <span className="w-1.5 h-1.5 rounded-full bg-slate-600" />,
        };
    }
  };

  const filteredStages = WORKFLOW_STAGES.filter(
    (stage) => !(project?.experiment_type === 'A' && stage.loop)
  );

  return (
    <div className="glass-panel rounded-2xl p-4 border border-slate-800/80 shadow-subtle-card space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/80">
        <div>
          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
            <Workflow className="w-3.5 h-3.5 text-indigo-400" />
            Execution Pipeline
          </h3>
          <p className="text-[11px] text-slate-400 mt-0.5">
            LangGraph Stage Tracker
          </p>
        </div>
        <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 font-mono border border-slate-700">
          {project?.experiment_type === 'A' ? 'Exp A' : 'Exp B'}
        </span>
      </div>

      {/* Stage Flow */}
      <div className="space-y-1 relative">
        {filteredStages.map((stage, idx, arr) => {
          const status = getStageStatus(stage.key, project, agentRuns);
          const style = getStageStyles(status);
          const isLoopStart = stage.key === 'tester';
          const isLoopEnd = stage.key === 'debugger';

          return (
            <div key={stage.key} className="relative">
              {/* Loop Bracket Announcement */}
              {isLoopStart && project?.experiment_type !== 'A' && (
                <div className="my-2 p-2 rounded-xl bg-purple-950/30 border border-purple-500/20 flex items-center justify-between text-[11px] text-purple-300">
                  <div className="flex items-center gap-1.5">
                    <Repeat className="w-3.5 h-3.5 text-purple-400" />
                    <span className="font-semibold">Feedback Loop:</span>
                    <span className="text-purple-400 font-mono text-[10px]">
                      Test ⇄ Review ⇄ Debug
                    </span>
                  </div>
                </div>
              )}

              {/* Stage Card */}
              <div
                onClick={() => {
                  if (stage.key === 'requirement') onNavigateTab?.('overview');
                  if (stage.key === 'coder') onNavigateTab?.('code');
                  if (stage.key === 'tester' || stage.key === 'reviewer' || stage.key === 'debugger')
                    onNavigateTab?.('iterations');
                  if (stage.key === 'evaluator') onNavigateTab?.('evaluation');
                  if (stage.key === 'approval') onNavigateTab?.('overview');
                }}
                className={`flex items-center justify-between p-2 rounded-xl border transition-all cursor-pointer ${style.card}`}
              >
                <div className="flex items-center gap-2 min-w-0">
                  <div
                    className={`w-6 h-6 rounded-lg flex items-center justify-center border shrink-0 ${style.iconBg}`}
                  >
                    {getStageIcon(stage.key)}
                  </div>
                  <div className="min-w-0">
                    <div className={`text-xs truncate ${style.text}`}>{stage.label}</div>
                  </div>
                </div>

                <div className="flex items-center gap-1 ml-2 shrink-0">
                  {style.badge}
                  <ChevronRight className="w-3 h-3 text-slate-600" />
                </div>
              </div>

              {/* Connector line */}
              {idx < arr.length - 1 && !isLoopEnd && (
                <div className="w-0.5 h-1 bg-slate-800 mx-auto my-0.5" />
              )}
            </div>
          );
        })}
      </div>

      {/* Quick Launch Actions */}
      <div className="pt-2 border-t border-slate-800/80 grid grid-cols-2 gap-2">
        <button
          onClick={() => onNavigateTab?.('code')}
          className="flex items-center justify-center gap-1.5 py-2 px-2 bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-700/80 rounded-xl text-xs font-semibold transition-all shadow-sm"
        >
          <Code2 className="w-3.5 h-3.5 text-indigo-400" />
          <span>Code Studio</span>
        </button>
        <button
          onClick={() => onNavigateTab?.('preview')}
          className="flex items-center justify-center gap-1.5 py-2 px-2 bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white rounded-xl text-xs font-semibold transition-all shadow-sm"
        >
          <MonitorPlay className="w-3.5 h-3.5" />
          <span>Live Preview</span>
        </button>
      </div>
    </div>
  );
};

