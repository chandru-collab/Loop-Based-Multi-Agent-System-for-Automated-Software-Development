import React from 'react';
import { CheckCircle2, Clock, AlertTriangle, XCircle, Sparkles, RefreshCw, Box } from 'lucide-react';

interface StatusBadgeProps {
  status: string;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className = '', size = 'md' }) => {
  const normalized = status?.toUpperCase() || 'UNKNOWN';

  const sizeClasses = {
    sm: 'text-[10px] px-2 py-0.5 gap-1',
    md: 'text-xs px-2.5 py-1 gap-1.5',
    lg: 'text-sm px-3.5 py-1.5 gap-2 font-medium',
  }[size];

  const getStyle = () => {
    switch (normalized) {
      case 'RUNNING':
        return {
          bg: 'bg-sky-950/70 text-sky-300 border-sky-500/30',
          icon: <RefreshCw className="w-3 h-3 animate-spin text-sky-400" />,
        };
      case 'COMPLETED':
        return {
          bg: 'bg-emerald-950/70 text-emerald-300 border-emerald-500/30',
          icon: <CheckCircle2 className="w-3 h-3 text-emerald-400" />,
        };
      case 'WAITING_FOR_APPROVAL':
        return {
          bg: 'bg-amber-950/70 text-amber-300 border-amber-500/30 animate-pulse-subtle',
          icon: <Clock className="w-3 h-3 text-amber-400" />,
        };
      case 'FAILED':
        return {
          bg: 'bg-rose-950/70 text-rose-300 border-rose-500/30',
          icon: <XCircle className="w-3 h-3 text-rose-400" />,
        };
      case 'PACKAGING':
        return {
          bg: 'bg-purple-950/70 text-purple-300 border-purple-500/30',
          icon: <Box className="w-3 h-3 text-purple-400" />,
        };
      case 'CREATED':
        return {
          bg: 'bg-slate-800 text-slate-300 border-slate-700',
          icon: <Sparkles className="w-3 h-3 text-slate-400" />,
        };
      default:
        return {
          bg: 'bg-slate-800/80 text-slate-400 border-slate-700/60',
          icon: <AlertTriangle className="w-3 h-3 text-slate-400" />,
        };
    }
  };

  const style = getStyle();

  return (
    <span
      className={`inline-flex items-center font-medium rounded-full border transition-all ${style.bg} ${sizeClasses} ${className}`}
    >
      {style.icon}
      <span>{normalized.replace(/_/g, ' ')}</span>
    </span>
  );
};

