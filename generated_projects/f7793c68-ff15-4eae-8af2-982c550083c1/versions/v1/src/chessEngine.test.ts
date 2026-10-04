import { describe, it, expect } from 'vitest';
import { ChessGame } from './chessEngine';

describe('ChessGame', () => {
  it('should initialize with white turn', () => {
    const game = new ChessGame();
    expect(game.turn).toBe('white');
  });

  it('should toggle turn after move', () => {
    const game = new ChessGame();
    game.makeMove([6, 4], [4, 4]);
    expect(game.turn).toBe('black');
  });

  it('should reject invalid moves', () => {
    const game = new ChessGame();
    expect(game.makeMove([4, 4], [4, 4])).toBe(false);
  });
});