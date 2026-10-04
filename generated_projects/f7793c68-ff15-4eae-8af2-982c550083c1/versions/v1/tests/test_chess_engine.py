import pytest

# Mocking basic chess board logic to fulfill the python test requirement
class ChessBoard:
    def __init__(self):
        self.turn = "white"
        self.history = []

    def is_valid_move(self, start, end):
        if start == end:
            return False
        return True

    def make_move(self, start, end):
        if self.is_valid_move(start, end):
            self.history.append((start, end))
            self.turn = "black" if self.turn == "white" else "white"
            return True
        return False

@pytest.fixture
def board():
    return ChessBoard()

def test_initial_turn(board):
    assert board.turn == "white"

def test_valid_move_execution(board):
    success = board.make_move((6, 4), (4, 4))
    assert success is True
    assert board.turn == "black"
    assert len(board.history) == 1
    assert board.history[0] == ((6, 4), (4, 4))

def test_invalid_same_position_move(board):
    success = board.make_move((4, 4), (4, 4))
    assert success is False
    assert board.turn == "white"
    assert len(board.history) == 0

def test_turn_alternation(board):
    board.make_move((6, 0), (5, 0))
    assert board.turn == "black"
    board.make_move((1, 0), (2, 0))
    assert board.turn == "white"
    assert len(board.history) == 2
