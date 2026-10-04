import React from 'react';
import { Position, Piece as PieceType } from '../types/chess';
import { Piece } from './Piece';

interface SquareProps {
  position: Position;
  piece: PieceType | null;
  isDark: boolean;
  isSelected: boolean;
  isValidTarget: boolean;
  isLastMove: boolean;
  isKingInCheck: boolean;
  onClick: (position: Position) => void;
}

export const Square: React.FC<SquareProps> = ({
  position,
  piece,
  isDark,
  isSelected,
  isValidTarget,
  isLastMove,
  isKingInCheck,
  onClick,
}) => {
  // Determine background color based on board pattern and highlights
  let bgColor = isDark ? 'bg-amber-800/80' : 'bg-amber-200/90';

  if (isLastMove) {
    bgColor = isDark ? 'bg-yellow-700/60' : 'bg-yellow-300/80';
  }

  if (isSelected) {
    bgColor = 'bg-blue-500/60';
  }

  // Check if king is in check (red highlight)
  const isKing = piece?.type === 'king';
  const showCheckHighlight = isKingInCheck && isKing && piece.color === (isKingInCheck ? piece.color : '');

  return (
    <div
      onClick={() => onClick(position)}
      className={`relative flex items-center justify-center aspect-square select-none cursor-pointer transition-colors duration-150 ${bgColor}
        ${showCheckHighlight ? 'ring-4 ring-red-600 animate-pulse' : ''}
      `}
      aria-label={`Square ${String.fromCharCode(97 + position.col)}${8 - position.row}`}
    >
      {/* Valid Move Indicator Marker */}
      {isValidTarget && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          {piece ? (
            // Capture ring
            <div className="w-full h-full border-4 border-red-500/70 rounded-full animate-pulse" />
          ) : (
            // Move dot
            <div className="w-4 h-4 bg-emerald-600/70 rounded-full shadow-md" />
          )}
        </div>
      )}

      {/* Chess Piece */}
      {piece && <Piece piece={piece} />}

      {/* Rank and File labels for board edge */}
      {position.col === 0 && (
        <span className="absolute top-1 left-1 text-[10px] font-bold opacity-60 pointer-events-none text-gray-800">
          {8 - position.row}
        </span>
      )}
      {position.row === 7 && (
        <span className="absolute bottom-1 right-1 text-[10px] font-bold opacity-60 pointer-events-none text-gray-800">
          {String.fromCharCode(97 + position.col)}
        </span>
      )}
    </div>
  );
};
