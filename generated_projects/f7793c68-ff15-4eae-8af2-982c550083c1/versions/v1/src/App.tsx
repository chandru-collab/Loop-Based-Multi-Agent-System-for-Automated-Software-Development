import React, { useState } from 'react';
import { ChessEngine } from './engine/chessEngine';

export default function App() {
  const [engine] = useState(new ChessEngine());
  const [board, setBoard] = useState(engine.board);
  const [turn, setTurn] = useState(engine.turn);

  const handleMove = (r: number, c: number) => {
    // Simplified interaction logic
    console.log(`Selected ${r}, ${c}`);
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold">Chess Game</h1>
      <p>Current Turn: {turn === 'w' ? 'White' : 'Black'}</p>
      <div className="grid grid-cols-8 w-96 border">
        {board.map((row, r) => row.map((sq, c) => (
          <div key={`${r}-${c}`} onClick={() => handleMove(r, c)} className="w-12 h-12 border flex items-center justify-center">
            {sq.piece}
          </div>
        )))}
      </div>
    </div>
  );
}