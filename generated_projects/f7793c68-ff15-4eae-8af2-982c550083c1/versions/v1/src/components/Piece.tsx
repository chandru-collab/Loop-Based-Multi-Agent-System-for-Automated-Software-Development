import React from 'react';
import { Piece as PieceType, PieceType as PType, Color } from '../types/chess';

interface PieceProps {
  piece: PieceType;
  isSelected?: boolean;
  isDragging?: boolean;
}

// Unicode chess symbols for clear, high-contrast visual representation
const PIECE_SYMBOLS: Record<Color, Record<PType, string>> = {
  white: {
    pawn: '♙',
    rook: '♔',
    knight: '♘',
    bishop: '♗',
    queen: '♕',
    king: '♔',
  },
  black: {
    pawn: '♟',
    rook: '♜',
    knight: '♞',
    bishop: '♝',
    queen: '♛',
    king: '♚',
  },
};

export const Piece: React.FC<PieceProps> = ({ piece, isSelected = false, isDragging = false }) => {
  const symbol = PIECE_SYMBOLS[piece.color][piece.type];

  return (
    <div
      className={`
        flex items-center justify-center w-full h-full select-none cursor-pointer
        transition-transform duration-150 ease-in-out
        ${piece.color === 'white' ? 'text-white drop-shadow-[0_2px_2px_rgba(0,0,0,0.8)]' : 'text-neutral-900 drop-shadow-[0_1px_1px_rgba(255,255,255,0.4)]'}
        ${isSelected ? 'scale-110 -translate-y-1' : 'hover:scale-105'}
        ${isDragging ? 'opacity-50 scale-125' : 'opacity-100'}
      `}
      aria-label={`${piece.color} ${piece.type}`}
    >
      <span className="text-3xl sm:text-4xl md:text-5xl font-bold leading-none">
        {symbol}
      </span>
    </div>
  );
};
