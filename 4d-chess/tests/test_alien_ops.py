from game.board import Board
from game.pieces.alien import Alien
from game.pieces.standard_pieces import Pawn


def test_alien_swap_axis_operation():
    board = Board((3, 3, 3, 3))
    alien = Alien(0)
    pawn = Pawn(1)
    board.place_piece(alien, (0, 0, 0, 0))
    board.place_piece(pawn, (1, 0, 0, 0))
    board.apply_layout(alien, {"operation": "swap_axis", "axes": (0, 1)})
    assert board.shape == (3, 3, 3, 3)
    assert board.get_piece((0, 0, 0, 0)) is alien


def test_alien_reshape_operation_changes_shape():
    board = Board((4, 4, 4, 4))
    alien = Alien(0)
    pawn = Pawn(1)
    board.place_piece(alien, (0, 0, 0, 0))
    board.place_piece(pawn, (1, 0, 0, 0))
    board.apply_layout(alien, {"operation": "reshape_axis", "axis_pair": (0, 1), "new_shape": (2, 8, 4, 4)})
    assert board.shape == (2, 8, 4, 4)
    assert board.get_piece((0, 0, 0, 0)) is alien
