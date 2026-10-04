import React from 'react';
import { RotateCcw, Undo2, Play } from 'lucide-react';

interface GameControlsProps {
  onReset: () => void;
  onUndo: () => void;
  canUndo: boolean;
}

export const GameControls: React.FC<GameControlsProps> = ({
  onReset,
  onUndo,
  canUndo,
}) => {
  return (
    <div className="flex flex-wrap items-center justify-center gap-4 mt-6 p-4 bg-slate-800 rounded-xl shadow-lg border border-slate-700 max-w-md mx-auto">
      <button
        onClick={onNewGame}
        className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded-lg transition-colors shadow-md focus:outline-none focus:ring-2 focus:ring-indigo-400"
      >
        <Play className="w-4 h-4" />
        New Game
      </button>

      <button
        onClick={onUndo}
        disabled={!canUndo}
        className={`flex items-center gap-2 px-4 py-2 font-medium rounded-lg transition-colors shadow-md focus:outline-none focus:ring-2 ${
          canUndo
            ? 'bg-amber-600 hover:bg-amber-500 text-white focus:ring-amber-400'
            : 'bg-slate-700 text-slate-400 cursor-not-allowed'
        }`}
      >
        <Undo2 className="w-4 h-4" />
        Undo Move
      </button>

      <button
        onClick={onReset}
        className="flex items-center gap-2 px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white font-medium rounded-lg transition-colors shadow-md focus:outline-none focus:ring-2 focus:ring-rose-400"
      >
        <RotateCcw className="w-4 h-4" />
        Reset Board
      </button>
    </div>
  );
};

function onNewGame() {
  window.location.reload();
}
