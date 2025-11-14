"""Implementation of the Alien piece with layout powers."""
from __future__ import annotations

import itertools
from typing import List, Tuple

from game.pieces.base_piece import BasePiece
from game.rules import Coordinate, Move, MovementRules, add_coordinates, king_offsets, within_bounds


class Alien(BasePiece):
    """The Alien can manipulate the entire board layout."""

    def __init__(self, owner: int) -> None:
        super().__init__(owner=owner, name="Alien", symbol="A")

    def clone(self) -> "Alien":
        alien = Alien(self.owner)
        alien.scratched = self.scratched
        alien.has_moved = self.has_moved
        return alien

    def generate_moves(self, board, position: Coordinate, rules: MovementRules) -> List[Move]:
        moves: List[Move] = []
        # Local moves similar to a king
        for offset in king_offsets():
            target = add_coordinates(position, offset)
            if not within_bounds(target, rules.board_shape):
                continue
            occupant = board.get_piece(target)
            if occupant is None or occupant.owner != self.owner:
                move_type = "capture" if occupant else "move"
                moves.append(Move(piece=self, start=position, end=target, move_type=move_type, metadata={"capture": bool(occupant)}))
        # Layout operations
        moves.extend(self._layout_moves(rules))
        return moves

    def _layout_moves(self, rules: MovementRules) -> List[Move]:
        shape = rules.board_shape
        layout_moves: List[Move] = []
        axes = tuple(range(len(shape)))
        for perm in itertools.permutations(axes):
            if perm == axes:
                continue
            layout_moves.append(
                Move(
                    piece=self,
                    start=(-1, -1, -1, -1),
                    end=(-1, -1, -1, -1),
                    move_type="layout",
                    metadata={"operation": "transpose", "axes": perm},
                )
            )
        for i in axes:
            for j in axes:
                if i >= j:
                    continue
                layout_moves.append(
                    Move(
                        piece=self,
                        start=(-1, -1, -1, -1),
                        end=(-1, -1, -1, -1),
                        move_type="layout",
                        metadata={"operation": "swap_axis", "axes": (i, j)},
                    )
                )
        for src in axes:
            for dst in axes:
                if src == dst:
                    continue
                layout_moves.append(
                    Move(
                        piece=self,
                        start=(-1, -1, -1, -1),
                        end=(-1, -1, -1, -1),
                        move_type="layout",
                        metadata={"operation": "move_axis", "source": src, "destination": dst},
                    )
                )
        for i in axes:
            for j in axes:
                if i >= j:
                    continue
                product = shape[i] * shape[j]
                for factor in _factor_pairs(product):
                    new_shape = list(shape)
                    new_shape[i] = factor[0]
                    new_shape[j] = factor[1]
                    if tuple(new_shape) == shape:
                        continue
                    layout_moves.append(
                        Move(
                            piece=self,
                            start=(-1, -1, -1, -1),
                            end=(-1, -1, -1, -1),
                            move_type="layout",
                            metadata={
                                "operation": "reshape_axis",
                                "axis_pair": (i, j),
                                "new_shape": tuple(new_shape),
                            },
                        )
                    )
        return layout_moves


def _factor_pairs(number: int) -> List[Tuple[int, int]]:
    pairs: List[Tuple[int, int]] = []
    for i in range(1, number + 1):
        if number % i == 0:
            pairs.append((i, number // i))
    return pairs


__all__ = ["Alien"]
