"""Four-dimensional chess board implementation."""
from __future__ import annotations

from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from game.rules import Coordinate, within_bounds
from game.utils import tensor_ops


class Board:
    def __init__(self, shape: Coordinate) -> None:
        self.shape: Coordinate = shape
        self.grid = tensor_ops.create_tensor(shape, None)
        self.positions: Dict[object, Coordinate] = {}

    def reset(self) -> None:
        self.grid = tensor_ops.create_tensor(self.shape, None)
        self.positions.clear()

    def is_empty(self, position: Coordinate) -> bool:
        return self.get_piece(position) is None

    def get_piece(self, position: Coordinate):
        if not within_bounds(position, self.shape):
            return None
        cell = self.grid[position[0]][position[1]][position[2]][position[3]]
        return cell

    def place_piece(self, piece, position: Coordinate) -> None:
        if not within_bounds(position, self.shape):
            raise ValueError("Position out of bounds")
        if not self.is_empty(position):
            raise ValueError("Position already occupied")
        self.grid[position[0]][position[1]][position[2]][position[3]] = piece
        self.positions[piece] = position

    def move_piece(self, start: Coordinate, end: Coordinate) -> Optional[object]:
        piece = self.get_piece(start)
        if piece is None:
            raise ValueError("No piece at starting position")
        captured = self.get_piece(end)
        self.grid[end[0]][end[1]][end[2]][end[3]] = piece
        self.grid[start[0]][start[1]][start[2]][start[3]] = None
        self.positions[piece] = end
        if captured:
            self.positions.pop(captured, None)
        return captured

    def remove_piece(self, position: Coordinate) -> Optional[object]:
        piece = self.get_piece(position)
        if piece is None:
            return None
        self.grid[position[0]][position[1]][position[2]][position[3]] = None
        self.positions.pop(piece, None)
        return piece

    def remove_piece_object(self, piece) -> None:
        position = self.positions.pop(piece, None)
        if position:
            self.grid[position[0]][position[1]][position[2]][position[3]] = None

    def iter_positions(self) -> Iterator[Tuple[Coordinate, object]]:
        for x in range(self.shape[0]):
            for y in range(self.shape[1]):
                for z in range(self.shape[2]):
                    for w in range(self.shape[3]):
                        piece = self.grid[x][y][z][w]
                        if piece is not None:
                            yield (x, y, z, w), piece

    def to_dict(self) -> Dict[str, object]:
        pieces = []
        for position, piece in self.iter_positions():
            pieces.append(
                {
                    "type": piece.__class__.__name__,
                    "owner": piece.owner,
                    "position": position,
                    "scratched": getattr(piece, "scratched", False),
                    "has_moved": getattr(piece, "has_moved", False),
                }
            )
        return {"shape": self.shape, "pieces": pieces}

    def apply_layout(self, acting_piece, metadata: Dict[str, object]) -> None:
        if acting_piece not in self.positions:
            raise ValueError("Acting piece must be on the board")
        original_position = self.positions[acting_piece]
        self.remove_piece(original_position)
        operation = metadata["operation"]
        if operation == "transpose":
            axes = metadata["axes"]
            self.grid = tensor_ops.transpose(self.grid, axes)
            self.shape = tensor_ops.shape_of(self.grid)  # type: ignore[assignment]
        elif operation == "swap_axis":
            axis_a, axis_b = metadata["axes"]
            self.grid = tensor_ops.swap_axes(self.grid, axis_a, axis_b)
            self.shape = tensor_ops.shape_of(self.grid)  # type: ignore[assignment]
        elif operation == "move_axis":
            self.grid = tensor_ops.move_axis(self.grid, metadata["source"], metadata["destination"])
            self.shape = tensor_ops.shape_of(self.grid)  # type: ignore[assignment]
        elif operation == "reshape_axis":
            new_shape = metadata["new_shape"]
            self.grid = tensor_ops.reshape_tensor(self.grid, new_shape)
            self.shape = tuple(new_shape)  # type: ignore[assignment]
        else:
            raise ValueError(f"Unknown layout operation {operation}")
        self._rebuild_positions()
        occupant = self.get_piece(original_position)
        if occupant is not None:
            self.remove_piece(original_position)
        if not within_bounds(original_position, self.shape):
            raise ValueError("Layout operation invalidated acting piece position")
        if not self.is_empty(original_position):
            raise ValueError("Acting position must be empty after layout")
        self.grid[original_position[0]][original_position[1]][original_position[2]][original_position[3]] = acting_piece
        self.positions[acting_piece] = original_position

    def _rebuild_positions(self) -> None:
        self.positions.clear()
        for position, piece in self.iter_positions():
            self.positions[piece] = position

    @classmethod
    def from_dict(cls, data: Dict[str, object], piece_factory) -> "Board":
        shape = tuple(data["shape"])  # type: ignore[assignment]
        board = cls(shape)  # type: ignore[arg-type]
        for piece_data in data["pieces"]:
            piece = piece_factory(piece_data)
            board.grid[piece_data["position"][0]][piece_data["position"][1]][piece_data["position"][2]][piece_data["position"][3]] = piece
            board.positions[piece] = tuple(piece_data["position"])  # type: ignore[assignment]
        return board


__all__ = ["Board"]
