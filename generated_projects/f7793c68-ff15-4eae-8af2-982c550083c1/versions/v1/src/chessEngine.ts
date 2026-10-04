export type Piece = 'p' | 'r' | 'n' | 'b' | 'q' | 'k';
export type Color = 'white' | 'black';
export interface Square { piece: Piece | null; color: Color | null; }
export type Board = Square[][];

export class ChessGame {
  board: Board;
  turn: Color = 'white';
  history: string[] = [];

  constructor() {
    this.board = Array(8).fill(null).map(() => Array(8).fill({ piece: null, color: null }));
  }

  isValidMove(from: [number, number], to: [number, number]): boolean {
    const [r1, c1] = from;
    const [r2, c2] = to;
    if (r1 === r2 && c1 === c2) return false;
    if (r1 < 0 || r1 > 7 || c1 < 0 || c1 > 7 || r2 < 0 || r2 > 7 || c2 < 0 || c2 > 7) return false;
    return true;
  }

  makeMove(from: [number, number], to: [number, number]): boolean {
    if (!this.isValidMove(from, to)) return false;
    this.history.push(`${from}->${to}`);
    this.turn = this.turn === 'white' ? 'black' : 'white';
    return true;
  }
}