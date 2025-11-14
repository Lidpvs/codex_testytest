"""Base class for all chess pieces."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, TYPE_CHECKING

from game.rules import Coordinate, Move, MovementRules, add_coordinates, within_bounds

if TYPE_CHECKING:
    from game.board import Board


@dataclass(unsafe_hash=True)
class BasePiece:
    owner: int
    name: str
    symbol: str
    scratched: bool = False
    has_moved: bool = False

    def clone(self) -> "BasePiece":
        return type(self)(self.owner)  # type: ignore[call-arg]

    def get_moves(self, board: "Board", position: Coordinate, rules: MovementRules) -> List[Move]:
        if self.scratched and not isinstance(self, PawnAdapter):
            adapter = PawnAdapter(self.owner, name=f"Scratched-{self.name}", symbol=self.symbol.lower())
            adapter.has_moved = self.has_moved
            return adapter.generate_pawn_moves(board, position, rules)
        return self.generate_moves(board, position, rules)

    def generate_moves(self, board: "Board", position: Coordinate, rules: MovementRules) -> List[Move]:
        raise NotImplementedError

    def mark_scratched(self) -> None:
        self.scratched = True


class PawnAdapter(BasePiece):
    def __init__(self, owner: int, name: str = "Pawn", symbol: str = "P") -> None:
        super().__init__(owner=owner, name=name, symbol=symbol)

    def generate_moves(self, board: "Board", position: Coordinate, rules: MovementRules) -> List[Move]:
        return self.generate_pawn_moves(board, position, rules)

    def generate_pawn_moves(self, board: "Board", position: Coordinate, rules: MovementRules) -> List[Move]:
        moves: List[Move] = []
        profile = rules.pawn_directions[self.owner]
        forward = [0, 0, 0, 0]
        forward[profile.axis] = profile.direction
        forward_tuple: Coordinate = tuple(forward)  # type: ignore[assignment]
        one_step = add_coordinates(position, forward_tuple)
        if within_bounds(one_step, rules.board_shape) and board.is_empty(one_step):
            moves.append(Move(piece=self, start=position, end=one_step))
            if not self.has_moved and profile.is_home(position):
                two_step = add_coordinates(one_step, forward_tuple)
                if within_bounds(two_step, rules.board_shape) and board.is_empty(two_step):
                    moves.append(Move(piece=self, start=position, end=two_step))
        # Capture moves
        for axis in range(len(position)):
            if axis == profile.axis:
                continue
            for side in (-1, 1):
                offset = list(forward_tuple)
                offset[axis] = side
                target = add_coordinates(position, tuple(offset))  # type: ignore[arg-type]
                if not within_bounds(target, rules.board_shape):
                    continue
                target_piece = board.get_piece(target)
                if target_piece and target_piece.owner != self.owner:
                    moves.append(Move(piece=self, start=position, end=target, move_type="capture", metadata={"capture": True}))
        return moves


__all__ = ["BasePiece", "PawnAdapter"]
