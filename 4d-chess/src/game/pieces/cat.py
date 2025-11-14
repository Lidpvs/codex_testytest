"""Implementation of the Cat piece."""
from __future__ import annotations

from typing import List, Set, Tuple

from game.pieces.base_piece import BasePiece
from game.rules import Coordinate, Move, MovementRules, add_coordinates, within_bounds


class Cat(BasePiece):
    """The Cat jumps between dimensions and can scratch pieces."""

    def __init__(self, owner: int) -> None:
        super().__init__(owner=owner, name="Cat", symbol="C")

    def clone(self) -> "Cat":
        cat = Cat(self.owner)
        cat.scratched = self.scratched
        cat.has_moved = self.has_moved
        return cat

    def generate_moves(self, board, position: Coordinate, rules: MovementRules) -> List[Move]:
        moves: List[Move] = []
        seen: Set[Coordinate] = set()
        # Jump by swapping dimensions while keeping other coordinates
        axes = range(len(position))
        for i in axes:
            for j in axes:
                if i >= j:
                    continue
                permuted = list(position)
                permuted[i], permuted[j] = permuted[j], permuted[i]
                target = tuple(permuted)  # type: ignore[assignment]
                if target == position or target in seen:
                    continue
                seen.add(target)
                moves.extend(self._move_or_scratch(board, position, target))
        # Move along a line while exchanging dimensional influence
        max_delta = max(rules.board_shape)
        for axis_from in axes:
            for axis_to in axes:
                if axis_from == axis_to:
                    continue
                for delta in range(-max_delta + 1, max_delta):
                    if delta == 0:
                        continue
                    vector = [0, 0, 0, 0]
                    vector[axis_from] = delta
                    vector[axis_to] = -delta
                    target = add_coordinates(position, tuple(vector))  # type: ignore[arg-type]
                    if target == position or target in seen:
                        continue
                    if not within_bounds(target, rules.board_shape):
                        continue
                    seen.add(target)
                    moves.extend(self._move_or_scratch(board, position, target))
        return moves

    def _move_or_scratch(self, board, start: Coordinate, target: Coordinate) -> List[Move]:
        occupant = board.get_piece(target)
        if occupant is None:
            return [Move(piece=self, start=start, end=target)]
        if occupant.owner == self.owner:
            return []
        return [Move(piece=self, start=start, end=target, move_type="scratch", metadata={"target": target})]


__all__ = ["Cat"]
