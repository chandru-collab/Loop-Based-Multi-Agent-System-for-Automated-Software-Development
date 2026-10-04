export type Piece = 'p' | 'r' | 'n' | 'b' | 'q' | 'k';
export type Color = 'w' | 'b';
export interface Square { piece: Piece | null; color: Color | null; }
export type Board = Square[][];

export class ChessEngine {
  board: Board;
  turn: Color = 'w';
  history: string[] = [];

  constructor() {
    this.board = Array(8).fill(null).map(() => Array(8).fill({ piece: null, color: null }));
    this.setupBoard();
  }

  private setupBoard() {
    const layout: Piece[] = ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'];
    for (let i = 0; i < 8; i++) {
      this.board[0][i] = { piece: layout[i], color: 'b' };
      this.board[1][i] = { piece: 'p', color: 'b' };
      this.board[6][i] = { piece: 'p', color: 'w' };
      this.board[7][i] = { piece: layout[i], color: 'w' };
    }
  }

  move(from: [number, number], to: [number, number]): boolean {
    const [r1, c1] = from;
    const [r2, c2] = to;
    const piece = this.board[r1][c1];
    if (!piece.piece || piece.color !== this.turn) return false;
    this.board[r2][c2] = piece;
    this.board[r1][c1] = { piece: null, color: null };
    this.history.push(`${String.fromCharCode(97 + c1)}${8 - r1} to ${String.fromCharCode(97 + c2)}${8 - r2}`);
    this.turn = this.turn === 'w' ? 'b' : 'w';
    return true;
  }
}