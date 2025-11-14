"""Standard chess pieces extended to four dimensions."""
from __future__ import annotations

from typing import Iterable, List

from game.pieces.base_piece import BasePiece, PawnAdapter
from game.rules import (
    Coordinate,
    Move,
    MovementRules,
    add_coordinates,
    bishop_directions,
    king_offsets,
    knight_offsets,
    rook_directions,
    within_bounds,
)


class SlidingPiece(BasePiece):
    def generate_sliding_moves(self, board, position: Coordinate, rules: MovementRules, directions: Iterable[Coordinate]) -> List[Move]:
        moves: List[Move] = []
        for direction in directions:
            current = position
            while True:
                current = add_coordinates(current, direction)
                if not within_bounds(current, rules.board_shape):
                    break
                occupant = board.get_piece(current)
                if occupant is None:
                    moves.append(Move(piece=self, start=position, end=current))
                    continue
                if occupant.owner != self.owner:
                    moves.append(Move(piece=self, start=position, end=current, move_type="capture", metadata={"capture": True}))
                break
        return moves


class Rook(SlidingPiece):
    def __init__(self, owner: int) -> None:
        super().__init__(owner=owner, name="Rook", symbol="R")

    def generate_moves(self, board, position: Coordinate, rules: MovementRules) -> List[Move]:
        return self.generate_sliding_moves(board, position, rules, rook_directions())

    def clone(self) -> "Rook":
        return Rook(self.owner)


class Bishop(SlidingPiece):
    def __init__(self, owner: int) -> None:
        super().__init__(owner=owner, name="Bishop", symbol="B")

    def generate_moves(self, board, position: Coordinate, rules: MovementRules) -> List[Move]:
        return self.generate_sliding_moves(board, position, rules, bishop_directions())

    def clone(self) -> "Bishop":
        return Bishop(self.owner)


class Queen(SlidingPiece):
    def __init__(self, owner: int) -> None:
        super().__init__(owner=owner, name="Queen", symbol="Q")

    def generate_moves(self, board, position: Coordinate, rules: MovementRules) -> List[Move]:
        directions = rook_directions() + bishop_directions()
        return self.generate_sliding_moves(board, position, rules, directions)

    def clone(self) -> "Queen":
        return Queen(self.owner)


class King(BasePiece):
    def __init__(self, owner: int) -> None:
        super().__init__(owner=owner, name="King", symbol="K")

    def generate_moves(self, board, position: Coordinate, rules: MovementRules) -> List[Move]:
        moves: List[Move] = []
        for offset in king_offsets():
            target = add_coordinates(position, offset)
            if not within_bounds(target, rules.board_shape):
                continue
            occupant = board.get_piece(target)
            if occupant is None:
                moves.append(Move(piece=self, start=position, end=target))
            elif occupant.owner != self.owner:
                moves.append(Move(piece=self, start=position, end=target, move_type="capture", metadata={"capture": True}))
        return moves

    def clone(self) -> "King":
        return King(self.owner)


class Knight(BasePiece):
    def __init__(self, owner: int) -> None:
        super().__init__(owner=owner, name="Knight", symbol="N")

    def generate_moves(self, board, position: Coordinate, rules: MovementRules) -> List[Move]:
        moves: List[Move] = []
        for offset in knight_offsets():
            target = add_coordinates(position, offset)
            if not within_bounds(target, rules.board_shape):
                continue
            occupant = board.get_piece(target)
            if occupant is None or occupant.owner != self.owner:
                move_type = "capture" if occupant else "move"
                moves.append(Move(piece=self, start=position, end=target, move_type=move_type, metadata={"capture": bool(occupant)}))
        return moves

    def clone(self) -> "Knight":
        return Knight(self.owner)


class Pawn(PawnAdapter):
    def __init__(self, owner: int) -> None:
        super().__init__(owner=owner, name="Pawn", symbol="P")

    def clone(self) -> "Pawn":
        pawn = Pawn(self.owner)
        pawn.scratched = self.scratched
        pawn.has_moved = self.has_moved
        return pawn


__all__ = ["King", "Queen", "Rook", "Bishop", "Knight", "Pawn"]
