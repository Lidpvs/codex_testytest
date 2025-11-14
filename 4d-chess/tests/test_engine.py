from game.engine import GameEngine
from game.pieces.cat import Cat
from game.pieces.standard_pieces import King, Rook
from game.rules import MovementRules


def configure_custom_engine():
    engine = GameEngine(board_shape=(4, 4, 4, 4), num_players=2)
    engine.board.reset()
    engine._king_positions.clear()
    engine._captured = {0: [], 1: []}
    engine.active_players = [0, 1]
    king_white = King(0)
    king_black = King(1)
    engine.board.place_piece(king_white, (0, 0, 0, 0))
    engine.board.place_piece(king_black, (3, 3, 3, 3))
    engine._king_positions[0] = (0, 0, 0, 0)
    engine._king_positions[1] = (3, 3, 3, 3)
    engine.turn_index = 0
    engine.rules = MovementRules(engine.board.shape, engine.pawn_profiles)
    return engine


def test_engine_cat_scratch_and_move(tmp_path):
    engine = configure_custom_engine()
    cat = Cat(0)
    enemy = Rook(1)
    engine.board.place_piece(cat, (1, 1, 1, 1))
    engine.board.place_piece(enemy, (2, 0, 1, 1))
    result = engine.execute_move(0, (1, 1, 1, 1), (2, 0, 1, 1))
    assert "scratched" in result
    assert enemy.scratched

    # Save and load round-trip
    save_path = tmp_path / "save.json"
    engine.save(save_path.as_posix())
    loaded = GameEngine.load(save_path.as_posix())
    assert loaded.board.shape == engine.board.shape


def test_engine_move_piece():
    engine = configure_custom_engine()
    rook = Rook(0)
    engine.board.place_piece(rook, (0, 1, 0, 0))
    result = engine.execute_move(0, (0, 1, 0, 0), (1, 1, 0, 0))
    assert "moved" in result
