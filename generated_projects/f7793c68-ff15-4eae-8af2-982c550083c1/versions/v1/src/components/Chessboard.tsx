import React from 'react';
import { Board, Position } from '../types/chess';
import Square from './Square';

interface ChessboardProps {
  board: Board;
  selectedPosition: Position | null;
  validMoves: Position[];
  onSquareClick: (pos: Position) => void;
  isFlipped?: boolean;
}

export const Chessboard: React.FC<ChessboardProps> = ({
  board,
  selectedPosition,
  validMoves,
  onSquareClick,
  isFlipped = false,
}) => {
  const files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
  const ranks = ['8', '7', '6', '5', '4', '3', '2', '1'];

  const rowIndices = isFlipped ? [7, 6, 5, 4, 3, 2, 1, 0] : [0, 1, 2, 3, 4, 5, 6, 7];
  const colIndices = isFlipped ? [7, 6, 5, 4, 3, 2, 1, 0] : [0, 1, 2, 3, 4, 5, 6, 7];

  return (
    <div className="flex flex-col items-center select-none">
      <div className="relative border-4 border-amber-900 rounded-lg shadow-2xl overflow-hidden bg-amber-900">
        <div className="grid grid-cols-8 w-[320px] h-[320px] sm:w-[480px] sm:h-[480px] md:w-[560px] md:h-[560px]">
          {rowIndices.map((row) =>
            colIndices.map((col) => {
              const piece = board[row][col];
              const isLight = (row + col) % 2 === 0;
              const isSelected =
                selectedPosition?.row === row && selectedPosition?.col === col;
              const isValidMove = validMoves.some(
                (m) => m.row === row && m.col === col
              );

              return (
                <Square
                  key={`${row}-${col}`}
                  row={row}
                  col={col}
                  piece={piece}
                  isLight={isLight}
                  isSelected={isSelected}
                  isValidMove={isValidMove}
                  onClick={() => onSquareClick({ row, col })}
                />
              );
            })
          )}
        </div>

        {/* Rank labels (1-8) on left side */}
        <div className="absolute left-1 top-0 bottom-0 flex flex-col justify-around text-xs font-bold text-amber-900/60 pointer-events-none hidden sm:flex">
          {ranks.map((rank, idx) => (
            <span key={rank} className="h-full flex items-center">
              {isFlipped ? ranks[7 - idx] : rank}
            </span>
          ))}
        </div>

        {/* File labels (a-h) on bottom */}
        <div className="absolute bottom-1 left-0 right-0 flex justify-around text-xs font-bold text-amber-900/60 pointer-events-none hidden sm:flex px-6">
          {files.map((file, idx) => (
            <span key={file}>
              {isFlipped ? files[7 - idx] : file}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Chessboard;
