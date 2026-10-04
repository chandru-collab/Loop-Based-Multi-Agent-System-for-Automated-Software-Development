import { describe, it, expect } from 'vitest';
import { createInitialBoard, isValidMove, getValidMoves } from '../engine/validator';
import { Board, Piece, Position, Color } from '../types/chess';

// Helper to create an empty board
const createEmptyBoard = (): Board => {
  const board: Board = [];
  for (let r = 0; r < 8; r++) {
    const row: (Piece | null)[] = [];
    for (let c = 0; c < 8; c++) {
      row.push(null);
    }
    board.push(row);
  }
  return board;
};

describe('Move Validation Engine', () => {
  it('should initialize standard board correctly', () => {
    const board = createInitialBoard();
    expect(board[0][0]).toEqual({ type: 'rook', color: 'black' });
    expect(board[7][4]).toEqual({ type: 'king', color: 'white' });
  });

  describe('Pawn Validation', () => {
    it('should allow white pawn 1 or 2 squares forward from starting position', () => {
      const board = createInitialBoard();
      const from: Position = { row: 6, col: 4 }; // e2

      // 1 square forward
      expect(isValidMove(board, from, { row: 5, col: 4 }, 'white')).toBe(true);
      // 2 squares forward
      expect(isValidMove(board, from, { row: 4, col: 4 }, 'white')).toBe(true);
      // Invalid 3 squares
      expect(isValidMove(board, from, { row: 3, col: 4 }, 'white')).toBe(false);
    });

    it('should allow white pawn diagonal capture', () => {
      const board = createEmptyBoard();
      board[6][4] = { type: 'pawn', color: 'white' };
      board[5][3] = { type: 'pawn', color: 'black' }; // diagonal enemy

      const from: Position = { row: 6, col: 4 };
      expect(isValidMove(board, from, { row: 5, col: 3 }, 'white')).toBe(true);
      // Cannot capture straight ahead if occupied
      board[5][4] = { type: 'pawn', color: 'black' };
      expect(isValidMove(board, from, { row: 5, col: 4 }, 'white')).toBe(false);
    });

    it('should allow black pawn 1 or 2 squares forward from starting position', () => {
      const board = createInitialBoard();
      const from: Position = { row: 1, col: 3 }; // d7

      expect(isValidMove(board, from, { row: 2, col: 3 }, 'black')).toBe(true);
      expect(isValidMove(board, from, { row: 3, col: 3 }, 'black')).toBe(true);
    });
  });

  describe('Knight Validation', () => {
    it('should allow L-shape moves and jumping over pieces', () => {
      const board = createInitialBoard();
      const from: Position = { row: 7, col: 1 }; // b1 knight

      // Valid L-shape over pawns
      expect(isValidMove(board, from, { row: 5, col: 2 }, 'white')).toBe(true);
      expect(isValidMove(board, from, { row: 5, col: 0 }, 'white')).toBe(true);

      // Invalid move
      expect(isValidMove(board, from, { row: 6, col: 1 }, 'white')).toBe(false);
    });
  });

  describe('Rook Validation', () => {
    it('should allow straight horizontal and vertical moves when path is clear', () => {
      const board = createEmptyBoard();
      board[4][4] = { type: 'rook', color: 'white' };

      const from: Position = { row: 4, col: 4 };

      // Vertical moves
      expect(isValidMove(board, from, { row: 0, col: 4 }, 'white')).toBe(true);
      expect(isValidMove(board, from, { row: 7, col: 4 }, 'white')).toBe(true);

      // Horizontal moves
      expect(isValidMove(board, from, { row: 4, col: 0 }, 'white')).toBe(true);
      expect(isValidMove(board, from, { row: 4, col: 7 }, 'white')).toBe(true);

      // Invalid diagonal
      expect(isValidMove(board, from, { row: 2, col: 2 }, 'white')).toBe(false);
    });

    it('should be blocked by pieces in its path', () => {
      const board = createEmptyBoard();
      board[4][4] = { type: 'rook', color: 'white' };
      board[4][6] = { type: 'pawn', color: 'white' }; // blocking friendly piece

      const from: Position = { row: 4, col: 4 };
      expect(isValidMove(board, from, { row: 4, col: 7 }, 'white')).toBe(false);
    });
  });

  describe('Bishop Validation', () => {
    it('should allow diagonal moves when clear', () => {
      const board = createEmptyBoard();
      board[4][4] = { type: 'bishop', color: 'white' };

      const from: Position = { row: 4, col: 4 };

      expect(isValidMove(board, from, { row: 1, col: 1 }, 'white')).toBe(true);
      expect(isValidMove(board, from, { row: 7, col: 7 }, 'white')).toBe(true);

      // Invalid straight
      expect(isValidMove(board, from, { row: 4, col: 6 }, 'white')).toBe(false);
    });
  });

  describe('Queen Validation', () => {
    it('should allow both straight and diagonal moves', () => {
      const board = createEmptyBoard();
      board[4][4] = { type: 'queen', color: 'white' };

      const from: Position = { row: 4, col: 4 };

      expect(isValidMove(board, from, { row: 4, col: 0 }, 'white')).toBe(true); // rook-like
      expect(isValidMove(board, from, { row: 0, col: 0 }, 'white')).toBe(true); // bishop-like
      expect(isValidMove(board, from, { row: 3, col: 2 }, 'white')).toBe(false); // invalid knight-like
    });
  });

  describe('King Validation', () => {
    it('should allow 1 square in any direction', () => {
      const board = createEmptyBoard();
      board[4][4] = { type: 'king', color: 'white' };

      const from: Position = { row: 4, col: 4 };

      expect(isValidMove(board, from, { row: 3, col: 4 }, 'white')).toBe(true);
      expect(isValidMove(board, from, { row: 3, col: 5 }, 'white')).toBe(true);
      expect(isValidMove(board, from, { row: 4, col: 5 }, 'white')).toBe(true);
      expect(isValidMove(board, from, { row: 5, col: 5 }, 'white')).toBe(true);
      expect(isValidMove(board, from, { row: 5, col: 4 }, 'white')).toBe(true);

      // Invalid 2 squares
      expect(isValidMove(board, from, { row: 2, col: 4 }, 'white')).toBe(false);
    });
  });

  describe('Turn and Boundary Rules', () => {
    it('should reject moves for the wrong player color', () => {
      const board = createInitialBoard();
      const from: Position = { row: 0, col: 0 }; // black rook

      // Trying to move black piece when turn is white
      expect(isValidMove(board, from, { row: 2, col: 0 }, 'white')).toBe(false);
    });

    it('should reject capturing own pieces', () => {
      const board = createInitialBoard();
      const from: Position = { row: 7, col: 0 }; // white rook
      const to: Position = { row: 7, col: 1 };   // white knight

      expect(isValidMove(board, from, to, 'white')).toBe(false);
    });

    it('should retrieve list of valid moves for a given piece', () => {
      const board = createEmptyBoard();
      board[4][4] = { type: 'rook', color: 'white' };
      const validMoves = getValidMoves(board, { row: 4, col: 4 });
      expect(validMoves.length).toBe(14);
    });
  });
});
