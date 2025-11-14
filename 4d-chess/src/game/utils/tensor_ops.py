"""Lightweight tensor manipulation utilities for 4D chess."""
from __future__ import annotations

from typing import Iterable, Iterator, List, Sequence, Tuple, Any


def shape_of(tensor: Sequence) -> Tuple[int, ...]:
    dims: List[int] = []
    current: Any = tensor
    while isinstance(current, list):
        dims.append(len(current))
        if len(current) == 0:
            break
        current = current[0]
    return tuple(dims)


def create_tensor(shape: Sequence[int], fill: Any = None) -> List:
    if not shape:
        return fill
    first, *rest = shape
    return [create_tensor(rest, fill) for _ in range(first)]


def iterate_indices(shape: Sequence[int]) -> Iterator[Tuple[int, ...]]:
    if not shape:
        yield ()
        return
    first, *rest = shape
    for idx in range(first):
        for sub in iterate_indices(rest):
            yield (idx, *sub)


def get_value(tensor: Sequence, index: Sequence[int]) -> Any:
    value = tensor
    for axis in index:
        value = value[axis]
    return value


def set_value(tensor: Sequence, index: Sequence[int], value: Any) -> None:
    target = tensor
    for axis in index[:-1]:
        target = target[axis]
    target[index[-1]] = value


def flatten(tensor: Sequence) -> List[Any]:
    if not isinstance(tensor, list):
        return [tensor]
    result: List[Any] = []
    for item in tensor:
        result.extend(flatten(item))
    return result


def reshape(flat_data: Iterable[Any], shape: Sequence[int]) -> List:
    iterator = iter(flat_data)

    def _build(current_shape: Sequence[int]) -> List:
        if not current_shape:
            return next(iterator)
        first, *rest = current_shape
        return [_build(rest) for _ in range(first)]

    total = 1
    for dim in shape:
        total *= dim
    flat_list = list(flat_data)
    if len(flat_list) != total:
        raise ValueError("Total size mismatch when reshaping tensor")
    iterator = iter(flat_list)
    return _build(shape)


def transpose(tensor: Sequence, axes: Sequence[int]) -> List:
    original_shape = shape_of(tensor)
    if sorted(axes) != list(range(len(original_shape))):
        raise ValueError("Invalid axes permutation for transpose")
    new_shape = tuple(original_shape[axis] for axis in axes)
    result = create_tensor(new_shape, None)
    for index in iterate_indices(original_shape):
        new_index = tuple(index[axis] for axis in axes)
        set_value(result, new_index, get_value(tensor, index))
    return result


def swap_axes(tensor: Sequence, axis_a: int, axis_b: int) -> List:
    axes = list(range(len(shape_of(tensor))))
    axes[axis_a], axes[axis_b] = axes[axis_b], axes[axis_a]
    return transpose(tensor, axes)


def move_axis(tensor: Sequence, source: int, destination: int) -> List:
    axes = list(range(len(shape_of(tensor))))
    axis = axes.pop(source)
    axes.insert(destination, axis)
    return transpose(tensor, axes)


def reshape_tensor(tensor: Sequence, new_shape: Sequence[int]) -> List:
    return reshape(flatten(tensor), new_shape)


def roll_axis(tensor: Sequence, axis: int, shift: int) -> List:
    shape = shape_of(tensor)
    axis_len = shape[axis]
    shift = shift % axis_len
    if shift == 0:
        return [row[:] if isinstance(row, list) else row for row in tensor]

    # Move axis to front, rotate, then move back
    moved = move_axis(tensor, axis, 0)
    rotated = moved[shift:] + moved[:shift]
    return move_axis(rotated, 0, axis)


__all__ = [
    "shape_of",
    "create_tensor",
    "iterate_indices",
    "get_value",
    "set_value",
    "flatten",
    "reshape",
    "transpose",
    "swap_axes",
    "move_axis",
    "reshape_tensor",
    "roll_axis",
]
