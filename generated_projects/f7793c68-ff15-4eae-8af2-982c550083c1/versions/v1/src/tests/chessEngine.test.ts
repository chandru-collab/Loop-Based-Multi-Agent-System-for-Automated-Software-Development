import { describe, it, expect, beforeEach } from 'vitest';
import { ChessEngine } from '../engine/chessEngine';

describe('ChessEngine State and Turn Mechanics', () => {
  let engine: ChessEngine;

  beforeEach(() => {
    engine = new ChessEngine();
  });

  it('should initialize with standard starting position and white turn', () => {
    expect(engine.turn).toBe('white');
    const board = engine.getBoard();
    // Check white rook at a1
    expect(board[7][0]).toEqual({ type: 'rook', color: 'white', hasMoved: false });
    // Check black king at e8
    expect(board[0][4]).toEqual({ type: 'king', color: 'black', hasMoved: false });
    // Check empty square at e4
    expect(board[4][4]).toBeNull();
  });

  it('should successfully make a valid move and switch turns', () => {
    // Move white pawn from e2 to e4
    const success = engine.makeMove({ row: 6, col: 4 }, { row: 4, col: 4 });
    expect(success).toBe(true);
    expect(engine.turn).toBe('black');
    
    const board = engine.getBoard();
    expect(board[6][4]).toBeNull();
    expect(board[4][4]).toEqual({ type: 'pawn', color: 'white', hasMoved: true });
  });

  it('should reject moving opponent pieces on wrong turn', () => {
    // White's turn, try to move black pawn from e7 to e5
    const success = engine.makeMove({ row: 1, col: 4 }, { row: 3, col: 4 });
    expect(success).toBe(false);
    expect(engine.turn).toBe('white');
    
    const board = engine.getBoard();
    expect(board[1][4]).toEqual({ type: 'pawn', color: 'black', hasMoved: false });
    expect(board[3][4]).toBeNull();
  });

  it('should record moves in history correctly', () => {
    engine.makeMove({ row: 6, col: 4 }, { row: 4, col: 4 }); // e4
    engine.makeMove({ row: 1, col: 4 }, { row: 3, col: 4 }); // e5

    const history = engine.getMoveHistory();
    expect(history.length).toBe(2);
    expect(history[0].notation).toBe('e4');
    expect(history[0].color).toBe('white');
    expect(history[1].notation).toBe('e5');
    expect(history[1].color).toBe('black');
  });

  it('should allow resetting the game', () => {
    engine.makeMove({ row: 6, col: 4 }, { row: 4, col: 4 });
    expect(engine.getMoveHistory().length).toBe(1);
    expect(engine.turn).toBe('black');

    engine.resetGame();
    expect(engine.turn).toBe('white');
    expect(engine.getMoveHistory().length).toBe(0);
    const board = engine.getBoard();
    expect(board[6][4]).toEqual({ type: 'pawn', color: 'white', hasMoved: false });
  });
});
