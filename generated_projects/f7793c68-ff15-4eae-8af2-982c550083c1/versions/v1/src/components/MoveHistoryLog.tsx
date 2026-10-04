import React, { useEffect, useRef } from 'react';
import { MoveRecord } from '../types/chess';

interface MoveHistoryLogProps {
  history: MoveRecord[];
}

export const MoveHistoryLog: React.FC<MoveHistoryLogProps> = ({ history }) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to the bottom of the log when new moves are added
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [history]);

  // Group moves into pairs (White move, Black move)
  const movePairs: Array<{ white?: MoveRecord; black?: MoveRecord }> = [];
  for (let i = 0; i < history.length; i += 2) {
    movePairs.push({
      white: history[i],
      black: history[i + 1],
    });
  }

  return (
    <div className="bg-slate-800 rounded-lg shadow-lg border border-slate-700 flex flex-col h-full max-h-96 w-full">
      <div className="px-4 py-3 border-b border-slate-700 bg-slate-900/50 rounded-t-lg">
        <h3 className="font-semibold text-slate-200 text-sm tracking-wide uppercase">
          Move History
        </h3>
      </div>
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 space-y-1 scrollbar-thin scrollbar-thumb-slate-600"
      >
        {movePairs.length === 0 ? (
          <p className="text-slate-400 text-sm italic text-center py-6">
            No moves played yet.
          </p>
        ) : (
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="text-slate-400 border-b border-slate-700/50">
                <th className="pb-2 w-12 font-medium">#</th>
                <th className="pb-2 font-medium">White</th>
                <th className="pb-2 font-medium">Black</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/30 font-mono">
              {movePairs.map((pair, index) => (
                <tr key={index} className="hover:bg-slate-700/20 transition-colors">
                  <td className="py-2 text-slate-500 font-semibold">{index + 1}.</td>
                  <td className="py-2 text-slate-200 font-medium">
                    {pair.white?.san || ''}
                  </td>
                  <td className="py-2 text-slate-200 font-medium">
                    {pair.black?.san || ''}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
      <div className="px-4 py-2 bg-slate-900/30 border-t border-slate-700/50 rounded-b-lg text-xs text-slate-400 text-right">
        Total moves: {history.length}
      </div>
    </div>
  );
};
