from game.board import Board
from game.pieces.cat import Cat
from game.pieces.standard_pieces import Knight, Pawn, Rook
from game.rules import MovementProfile, MovementRules


BOARD_SHAPE = (4, 4, 4, 4)
RULES = MovementRules(
    BOARD_SHAPE,
    {
        0: MovementProfile(axis=0, direction=1, home_coordinates=(1,)),
        1: MovementProfile(axis=0, direction=-1, home_coordinates=(2,)),
    },
)


def prepare_board():
    return Board(BOARD_SHAPE)


def test_rook_moves_in_four_dimensions():
    board = prepare_board()
    rook = Rook(0)
    board.place_piece(rook, (1, 1, 1, 1))
    moves = rook.get_moves(board, (1, 1, 1, 1), RULES)
    assert len(moves) == 12  # three moves along each of four axes


def test_knight_has_4d_jump_moves():
    board = prepare_board()
    knight = Knight(0)
    board.place_piece(knight, (1, 1, 1, 1))
    moves = knight.get_moves(board, (1, 1, 1, 1), RULES)
    assert any(move.end == (3, 2, 1, 1) for move in moves)
    assert any(move.end == (0, 3, 1, 1) for move in moves)


def test_cat_generates_scratch_move():
    board = prepare_board()
    cat = Cat(0)
    enemy = Rook(1)
    board.place_piece(cat, (1, 1, 1, 1))
    board.place_piece(enemy, (2, 0, 1, 1))
    moves = cat.get_moves(board, (1, 1, 1, 1), RULES)
    scratch_moves = [move for move in moves if move.move_type == "scratch"]
    assert scratch_moves
    assert scratch_moves[0].end == (2, 0, 1, 1)
