# 4D Chess

A production-ready, fully playable four-dimensional chess engine with a text-based interface, special Cat and Alien pieces, and layout manipulation mechanics.

## What Is 4D Chess?

This project generalises classic chess onto a four-dimensional lattice. The board is represented as `board[x][y][z][w]`, where each axis can be independently sized. Pieces occupy discrete coordinates, and movement rules have been extended to respect the additional dimensions. Up to four players battle simultaneously, each aligned to a unique primary axis.

## Gameplay Overview

* **Board** – Configurable shape defined by a 4-tuple, defaulting to `(4, 4, 4, 4)`.
* **Players** – Supports 2–4 players. Each player receives a colour ID automatically.
* **Turns** – Round-robin order. Eliminated players are skipped.
* **Win Condition** – Capture of all opposing kings. When only one king remains on the board the owning player wins.
* **Movement** – Standard chess pieces adapt their movements to 4D vectors:
  * **King** – One step in any non-zero direction in 4D space.
  * **Queen** – Combination of rook and bishop vectors across four axes.
  * **Rook** – Slides along any single axis.
  * **Bishop** – Slides along multi-axis diagonals with equal step magnitudes.
  * **Knight** – Jumps using all permutations of the classic “two-and-one” offsets in 4D.
  * **Pawn** – Moves along its assigned axis, can advance two spaces from its home layer, and captures forward plus one step on exactly one other axis.

## Special Pieces

### Cat

The Cat is a dimensional acrobat:

* **Dimensional Jumps** – It can leap by swapping any pair of axes or by transferring distance from one axis into another while remaining on the same line (e.g., `+Δ` on `x` and `-Δ` on `y`).
* **Scratch Ability** – When targeting an opposing piece the Cat may scratch it instead of moving. A scratched piece permanently loses its original movement profile and can only move like a pawn for the remainder of the game. Scratching counts as the Cat’s turn but the Cat remains in place.

### Alien

The Alien bends reality. In addition to short king-like steps, it can transform the entire board layout while staying anchored to its current square.

Supported operations are applied to every piece except the acting Alien:

| Operation      | Description                                                                                       | Example Syntax                          |
| -------------- | ------------------------------------------------------------------------------------------------- | --------------------------------------- |
| `transpose`    | Reorder axes using a full permutation.                                                            | `layout transpose 1 0 2 3`              |
| `swap_axis`    | Swap two axes (convenience wrapper around `transpose`).                                           | `layout swap_axis 0 1`                  |
| `move_axis`    | Reposition an axis within the axis order (akin to NumPy `moveaxis`).                              | `layout move_axis 0 3`                  |
| `reshape_axis` | Reshape axis pairs into new lengths while preserving the total number of cells.                   | `layout reshape_axis 0 1 2 8 4 4`       |

These operations leverage a custom tensor toolkit that mimics NumPy-like behaviour without external dependencies.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

No external libraries are required; the project runs on pure Python.

## Running the Game

Start the interactive shell:

```bash
python -m cli.main --players 2 --shape 4 4 4 4
```

### Move Syntax Examples

* Show legal moves: `moves (1, 2, 1, 0)`
* Standard move: `move (1, 1, 1, 0) (2, 1, 1, 0)`
* Cat scratch attempt: `move (1, 1, 1, 1) (2, 0, 1, 1)`
* Alien transpose: `layout transpose 1 0 2 3`
* Save / load: `save game.json`, `load game.json`

Coordinates are always provided as `(x, y, z, w)` tuples.

## Architecture

```
src/
├── cli/               # Text-based UI
│   └── main.py
├── game/
│   ├── board.py       # 4D board state and tensor-aware layout operations
│   ├── engine.py      # Game orchestration, turns, validation, serialization
│   ├── pieces/
│   │   ├── base_piece.py
│   │   ├── standard_pieces.py
│   │   ├── cat.py
│   │   └── alien.py
│   └── utils/
│       └── tensor_ops.py  # NumPy-like tensor helpers (transpose, reshape, etc.)
└── tests/
```

Key design highlights:

* **Data-driven movement** – Movement vectors are computed algorithmically, avoiding large `if/else` chains.
* **Board tensor toolkit** – `tensor_ops` implements reshape, transpose, swap, and move axis primitives, enabling Alien abilities without third-party libraries.
* **Separation of concerns** – Pieces know how to generate moves; the engine validates, executes, and manages game state.

## Extending the Game

* Add new pieces by subclassing `BasePiece` and implementing `generate_moves`.
* Introduce new Alien operations by expanding `tensor_ops` and `Alien._layout_moves`.
* Customise starting layouts by editing `_setup_initial_state` inside `engine.py`.

## Testing

Run the automated test suite:

```bash
pytest
```

## License

This project is distributed under the **Meow Meow Creative Commons — Non-Commercial Use Only** license. See [LICENSE](LICENSE).
