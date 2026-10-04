import React from 'react';
import { Color, GameStatus } from '../types/chess';
import { Crown, AlertCircle, RefreshCw, Trophy } from 'lucide-react';

interface TurnIndicatorProps {
  turn: Color;
  status: GameStatus;
  winner: Color | null;
  onReset: () => void;
}

export const TurnIndicator: React.FC<TurnIndicatorProps> = ({
  turn,
  status,
  winner,
  onReset,
}) => {
  const renderStatusMessage = () => {
    switch (status) {
      case 'checkmate':
        return (
          <div className="flex items-center gap-2 text-red-600 font-bold">
            <Trophy className="w-5 h-5 animate-bounce" />
            <span>Checkmate! {winner === 'w' ? 'White' : 'Black'} wins!</span>
          </div>
        );
      case 'stalemate':
        return (
          <div className="flex items-center gap-2 text-amber-600 font-bold">
            <AlertCircle className="w-5 h-5" />
            <span>Stalemate - Draw!</span>
          </div>
        );
      case 'check':
        return (
          <div className="flex items-center gap-2 text-orange-600 font-bold animate-pulse">
            <AlertCircle className="w-5 h-5" />
            <span>Check! {turn === 'w' ? 'White' : 'Black'} is in check.</span>
          </div>
        );
      case 'active':
      default:
        return (
          <div className="flex items-center gap-2">
            <div
              className={`w-4 h-4 rounded-full border border-gray-400 shadow-inner ${
                turn === 'w' ? 'bg-white' : 'bg-gray-900'
              }`}
            />
            <span className="font-medium text-gray-700">
              {turn === 'w' ? "White's Turn" : "Black's Turn"}
            </span>
          </div>
        );
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-md p-4 flex flex-col sm:flex-row items-center justify-between gap-4 border border-gray-100">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
          <Crown className="w-6 h-6" />
        </div>
        <div>
          <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-400">
            Game Status
          </h2>
          <div className="text-lg mt-0.5">{renderStatusMessage()}</div>
        </div>
      </div>

      <button
        onClick={onReset}
        className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium text-sm transition-colors duration-200 active:scale-95"
        title="Restart Game"
      >
        <RefreshCw className="w-4 h-4" />
        <span>New Game</span>
      </button>
    </div>
  );
};
