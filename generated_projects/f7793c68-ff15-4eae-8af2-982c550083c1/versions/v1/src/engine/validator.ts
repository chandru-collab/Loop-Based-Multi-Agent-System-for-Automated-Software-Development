import { Board, Color, Move, Piece, PieceType, Position } from '../types/chess';

/**
 * Checks if a position is within the standard 8x8 chessboard boundaries.
 */
export function isValidPosition(pos: Position): boolean {
  return pos.row >= 0 && pos.row < 8 && pos.col >= 0 && pos.col < 8;
}

/**
 * Determines if two positions are identical.
 */
export function isSamePosition(a: Position, b: Position): boolean {
  return a.row === b.row && a.col === b.col;
}

/**
 * Gets the piece at a given position on the board.
 */
export function getPieceAt(board: Board, pos: Position): Piece | null {
  if (!isValidPosition(pos)) return null;
  return board[pos.row][pos.col];
}

/**
 * Checks if the path between start and end (exclusive of start, inclusive of end) is clear of pieces.
 * Used for sliding pieces: Rook, Bishop, Queen.
 */
export function isPathClear(board: Board, start: Position, end: Position): boolean {
  const rowDiff = end.row - start.row;
  const colDiff = end.col - start.col;

  const rowStep = rowDiff === 0 ? 0 : rowDiff > 0 ? 1 : -1;
  const colStep = colDiff === 0 ? 0 : colDiff > 0 ? 1 : -1;

  let currentRow = start.row + rowStep;
  let currentCol = start.col + colStep;

  while (currentRow !== end.row || currentCol !== end.col) {
    if (board[currentRow][currentCol] !== null) {
      return false;
    }
    currentRow += rowStep;
    currentCol += colStep;
  }

  return true;
}

/**
 * Validates specific piece movement patterns without considering checks.
 */
export function isValidPieceMove(board: Board, move: Move): boolean {
  const { from, to } = move;
  const piece = getPieceAt(board, from);
  const targetPiece = getPieceAt(board, to);

  if (!piece) return false;

  // Cannot capture your own piece
  if (targetPiece && targetPiece.color === piece.color) {
    return false;
  }

  const rowDiff = to.row - from.row;
  const colDiff = to.col - from.col;
  const absRowDiff = Math.abs(rowDiff);
  const absColDiff = Math.abs(colDiff);

  switch (piece.type) {
    case PieceType.PAWN: {
      const direction = piece.color === Color.WHITE ? -1 : 1;
      const startRow = piece.color === Color.WHITE ? 6 : 1;

      // Move forward 1 square
      if (colDiff === 0 && rowDiff === direction && !targetPiece) {
        return true;
      }

      // Move forward 2 squares from starting position
      if (
        colDiff === 0 &&
        rowDiff === direction * 2 &&
        from.row === startRow &&
        !targetPiece &&
        board[from.row + direction][from.col] === null
      ) {
        return true;
      }

      // Diagonal capture
      if (absColDiff === 1 && rowDiff === direction && targetPiece !== null) {
        return true;
      }

      return false;
    }

    case PieceType.KNIGHT: {
      return (absRowDiff === 2 && absColDiff === 1) || (absRowDiff === 1 && absColDiff === 2);
    }

    case PieceType.BISHOP: {
      if (absRowDiff === absColDiff) {
        return isPathClear(board, from, to);
      }
      return false;
    }

    case PieceType.ROOK: {
      if (rowDiff === 0 || colDiff === 0) {
        return isPathClear(board, from, to);
      }
      return false;
    }

    case PieceType.QUEEN: {
      if (rowDiff === 0 || colDiff === 0 || absRowDiff === absColDiff) {
        return isPathClear(board, from, to);
      }
      return false;
    }

    case PieceType.KING: {
      return absRowDiff <= 1 && absColDiff <= 1;
    }

    default:
      return false;
  }
}

/**
 * Finds the position of the king of a given color on the board.
 */
export function findKingPosition(board: Board, color: Color): Position | null {
  for (let r = 0; r < 8; r++) {
    for (let c = 0; c < 8; c++) {
      const piece = board[r][c];
      if (piece && piece.type === PieceType.KING && piece.color === color) {
        return { row: r, col: c };
      }
    }
  }
  return null;
}

/**
 * Checks if a specific player's king is currently under attack (in check).
 */
export function isKingInCheck(board: Board, color: Color): boolean {
  const kingPos = findKingPosition(board, color);
  if (!kingPos) return false; // Should not happen in a valid game

  const enemyColor = color === Color.WHITE ? Color.BLACK : Color.WHITE;

  for (let r = 0; r < 8; r++) {
    for (let c = 0; c < 8; c++) {
      const piece = board[r][c];
      if (piece && piece.color === enemyColor) {
        const simulatedMove: Move = {
          from: { row: r, col: c },
          to: kingPos,
          piece,
          captured: getPieceAt(board, kingPos)
        };
        if (isValidPieceMove(board, simulatedMove)) {
          return true;
        }
      }
    }
  }

  return false;
}

/**
 * Simulates making a move on a deep-copied board and returns the new board state.
 */
export function simulateMove(board: Board, move: Move): Board {
  const newBoard: Board = board.map(row => row.map(piece => (piece ? { ...piece } : null)));
  newBoard[move.to.row][move.to.col] = newBoard[move.from.row][move.from.col];
  newBoard[move.from.row][move.from.col] = null;
  return newBoard;
}

/**
 * Validates a move fully, including checking if the move leaves or puts the player's king in check.
 */
export function isValidMove(board: Board, move: Move, currentTurn: Color): boolean {
  const piece = getPieceAt(board, move.from);
  if (!piece) return false;

  // Verify turn
  if (piece.color !== currentTurn) return false;

  // Verify basic geometric/piece movement rules
  if (!isValidPieceMove(board, move)) return false;

  // Simulate move to ensure it doesn't leave the king in check
  const simulatedBoard = simulateMove(board, move);
  if (isKingInCheck(simulatedBoard, currentTurn)) {
    return false;
  }

  return true;
}

/**
 * Retrieves all valid moves for a given player.
 */
export function getAllValidMoves(board: Board, color: Color): Move[] {
  const validMoves: Move[] = [];

  for (let r = 0; r < 8; r++) {
    for (let c = 0; c < 8; c++) {
      const piece = board[r][c];
      if (piece && piece.color === color) {
        const from: Position = { row: r, col: c };
        for (let tr = 0; tr < 8; tr++) {
          for (let tc = 0; tc < 8; tc++) {
            const to: Position = { row: tr, col: tc };
            const move: Move = {
              from,
              to,
              piece,
              captured: getPieceAt(board, to)
            };
            if (isValidMove(board, move, color)) {
              validMoves.push(move);
            }
          }
        }
      }
    }
  }

  return validMoves;
}

/**
 * Checks if the current player is in checkmate.
 */
export function isCheckmate(board: Board, color: Color): boolean {
  if (!isKingInCheck(board, color)) return false;
  const validMoves = getAllValidMoves(board, color);
  return validMoves.length === 0;
}

/**
 * Checks if the current player is in stalemate (no valid moves, but not in check).
 */
export function isStalemate(board: Board, color: Color): boolean {
  if (isKingInCheck(board, color)) return false;
  const validMoves = getAllValidMoves(board, color);
  return validMoves.length === 0;
}
