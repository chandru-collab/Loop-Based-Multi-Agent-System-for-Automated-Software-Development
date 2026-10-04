export type PieceColor = 'white' | 'black';
export type PieceType = 'pawn' | 'rook' | 'knight' | 'bishop' | 'queen' | 'king';

export interface Piece {
  id: string;
  type: PieceType;
  color: PieceColor;
  hasMoved?: boolean;
}

export type SquareContent = Piece | null;

export type BoardState = SquareContent[][];

export interface Position {
  row: number;
  col: number;
}

export interface Move {
  from: Position;
  to: Position;
  piece: Piece;
  captured?: Piece | null;
  promotion?: PieceType;
  isCastling?: 'kingside' | 'queenside';
  isEnPassant?: boolean;
}

export interface MoveHistoryItem {
  id: string;
  move: Move;
  notation: string;
  timestamp: number;
}

export type GameStatus = 'active' | 'check' | 'checkmate' | 'stalemate' | 'draw';

export interface GameState {
  board: BoardState;
  turn: PieceColor;
  status: GameStatus;
  moveHistory: MoveHistoryItem[];
  capturedPieces: {
    white: Piece[];
    black: Piece[];
  };
  kingPositions: {
    white: Position;
    black: Position;
  };
  enPassantTarget: Position | null;
  halfMoveClock: number;
  fullMoveNumber: number;
}
