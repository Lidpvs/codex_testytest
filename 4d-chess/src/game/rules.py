"""Core rules and data structures for the 4D chess engine."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple

Coordinate = Tuple[int, int, int, int]


@dataclass(frozen=True)
class MovementProfile:
    axis: int
    direction: int
    home_coordinates: Tuple[int, ...]

    def is_home(self, position: Coordinate) -> bool:
        return position[self.axis] == self.home_coordinates[0]


@dataclass
class MovementRules:
    board_shape: Coordinate
    pawn_directions: Dict[int, MovementProfile]


@dataclass
class Move:
    piece: "BasePiece"
    start: Coordinate
    end: Coordinate
    move_type: str = "move"  # move, capture, scratch, layout
    metadata: Dict[str, object] = field(default_factory=dict)

    @property
    def is_capture(self) -> bool:
        return self.metadata.get("capture", False)

    def describe(self) -> str:
        meta = ""
        if self.move_type == "layout":
            meta = f" via {self.metadata.get('operation')}"
        elif self.move_type == "scratch":
            meta = " (scratch)"
        return f"{self.piece.name} {self.start} -> {self.end}{meta}"


def within_bounds(position: Coordinate, shape: Coordinate) -> bool:
    return all(0 <= coord < dim for coord, dim in zip(position, shape))


def add_coordinates(a: Coordinate, b: Coordinate) -> Coordinate:
    return tuple(x + y for x, y in zip(a, b))  # type: ignore[return-value]


def scale_coordinate(vector: Coordinate, scalar: int) -> Coordinate:
    return tuple(component * scalar for component in vector)  # type: ignore[return-value]


def king_offsets(dimensions: int = 4) -> List[Coordinate]:
    offsets: List[Coordinate] = []
    ranges = [-1, 0, 1]
    for x in ranges:
        for y in ranges:
            for z in ranges:
                for w in ranges:
                    if (x, y, z, w).count(0) == dimensions and (x, y, z, w) == (0,) * dimensions:
                        continue
                    if (x, y, z, w) != (0, 0, 0, 0):
                        offsets.append((x, y, z, w))
    return offsets


def rook_directions(dimensions: int = 4) -> List[Coordinate]:
    directions: List[Coordinate] = []
    basis = [0] * dimensions
    for axis in range(dimensions):
        vec = basis.copy()
        vec[axis] = 1
        directions.append(tuple(vec))
        vec = basis.copy()
        vec[axis] = -1
        directions.append(tuple(vec))
    return directions


def bishop_directions(dimensions: int = 4) -> List[Coordinate]:
    directions: List[Coordinate] = []
    values = [-1, 0, 1]
    for x in values:
        for y in values:
            for z in values:
                for w in values:
                    vec = (x, y, z, w)
                    if vec == (0, 0, 0, 0):
                        continue
                    non_zero = [component for component in vec if component != 0]
                    if len(non_zero) >= 2 and len(set(abs(component) for component in non_zero)) == 1:
                        directions.append(vec)
    return directions


def knight_offsets(dimensions: int = 4) -> List[Coordinate]:
    offsets: set[Coordinate] = set()
    base = [0] * dimensions
    axes = list(range(dimensions))
    for i in axes:
        for j in axes:
            if i == j:
                continue
            for sign_i in (-1, 1):
                for sign_j in (-1, 1):
                    vec = base.copy()
                    vec[i] = 2 * sign_i
                    vec[j] = 1 * sign_j
                    offsets.add(tuple(vec))
    return sorted(offsets)


def coordinate_to_string(coordinate: Coordinate) -> str:
    return f"({coordinate[0]}, {coordinate[1]}, {coordinate[2]}, {coordinate[3]})"


__all__ = [
    "Coordinate",
    "MovementProfile",
    "MovementRules",
    "Move",
    "within_bounds",
    "add_coordinates",
    "scale_coordinate",
    "king_offsets",
    "rook_directions",
    "bishop_directions",
    "knight_offsets",
    "coordinate_to_string",
]
