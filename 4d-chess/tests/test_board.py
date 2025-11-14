import pytest

from game.board import Board
from game.pieces.alien import Alien
from game.pieces.standard_pieces import Pawn


def test_place_and_move_piece():
    board = Board((3, 3, 3, 3))
    pawn = Pawn(0)
    board.place_piece(pawn, (0, 0, 0, 0))
    assert board.get_piece((0, 0, 0, 0)) is pawn
    board.move_piece((0, 0, 0, 0), (1, 0, 0, 0))
    assert board.get_piece((1, 0, 0, 0)) is pawn
    assert board.get_piece((0, 0, 0, 0)) is None


def test_layout_transpose_keeps_alien_fixed():
    board = Board((3, 3, 3, 3))
    alien = Alien(0)
    pawn = Pawn(1)
    board.place_piece(alien, (0, 0, 0, 0))
    board.place_piece(pawn, (1, 0, 0, 0))
    board.apply_layout(alien, {"operation": "transpose", "axes": (1, 0, 2, 3)})
    assert board.get_piece((0, 0, 0, 0)) is alien
    assert board.get_piece((0, 1, 0, 0)) is pawn
