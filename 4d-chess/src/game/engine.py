"""Main engine orchestrating the 4D chess game."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

from game.board import Board
from game.pieces.alien import Alien
from game.pieces.cat import Cat
from game.pieces.standard_pieces import Bishop, King, Knight, Pawn, Queen, Rook
from game.rules import Coordinate, Move, MovementProfile, MovementRules, coordinate_to_string, within_bounds


@dataclass
class Player:
    identifier: int
    name: str


class GameEngine:
    def __init__(self, board_shape: Coordinate = (4, 4, 4, 4), num_players: int = 2) -> None:
        if num_players < 2 or num_players > 4:
            raise ValueError("Number of players must be between 2 and 4")
        self.board = Board(board_shape)
        self.players: List[Player] = [Player(i, f"Player {i + 1}") for i in range(num_players)]
        self.turn_index: int = 0
        self.active_players: List[int] = [player.identifier for player in self.players]
        self.pawn_profiles: Dict[int, MovementProfile] = self._create_pawn_profiles()
        self.rules = MovementRules(board_shape, self.pawn_profiles)
        self._captured: Dict[int, List[str]] = {player.identifier: [] for player in self.players}
        self._king_positions: Dict[int, Coordinate] = {}
        self._setup_initial_state()

    # Player and turn management -------------------------------------------------
    @property
    def current_player_id(self) -> int:
        return self.active_players[self.turn_index % len(self.active_players)]

    def next_turn(self) -> None:
        if not self.active_players:
            return
        self.turn_index = (self.turn_index + 1) % len(self.active_players)

    # Setup ---------------------------------------------------------------------
    def _create_pawn_profiles(self) -> Dict[int, MovementProfile]:
        shape = self.board.shape
        profiles: Dict[int, MovementProfile] = {}
        def clamp_home(axis: int, positive: bool) -> int:
            dimension = shape[axis]
            if dimension <= 2:
                return max(0, dimension - 1)
            return 1 if positive else dimension - 2

        configurations = [
            MovementProfile(axis=0, direction=1, home_coordinates=(clamp_home(0, True),)),
            MovementProfile(axis=0, direction=-1, home_coordinates=(clamp_home(0, False),)),
            MovementProfile(axis=1, direction=1, home_coordinates=(clamp_home(1, True),)),
            MovementProfile(axis=1, direction=-1, home_coordinates=(clamp_home(1, False),)),
        ]
        for player in self.players:
            profiles[player.identifier] = configurations[player.identifier]
        return profiles

    def _setup_initial_state(self) -> None:
        occupied: set[Coordinate] = set()
        for player in self.players:
            axis = self.pawn_profiles[player.identifier].axis
            direction = self.pawn_profiles[player.identifier].direction
            back_value = 0 if direction > 0 else self.board.shape[axis] - 1
            pawn_value = back_value + direction
            back_positions = self._available_positions(axis, back_value, occupied)
            pawn_positions: List[Coordinate] = []
            if 0 <= pawn_value < self.board.shape[axis]:
                pawn_positions = list(self._available_positions(axis, pawn_value, occupied))
            self._deploy_back_rank(player.identifier, back_positions, occupied)
            if pawn_positions:
                self._deploy_pawns(player.identifier, pawn_positions, occupied)

    def _available_positions(self, axis: int, axis_value: int, occupied: set[Coordinate]) -> Iterable[Coordinate]:
        ranges = [self._ordered_axis_values(i, axis) for i in range(4)]
        for coord in self._iterate_coordinates(ranges):
            if coord[axis] != axis_value:
                continue
            if coord in occupied:
                continue
            yield coord

    def _ordered_axis_values(self, axis_index: int, orientation_axis: int) -> List[int]:
        dimension = self.board.shape[axis_index]
        values = list(range(dimension))
        # Prefer interior coordinates to reduce conflicts between orientations
        center_order = sorted(values, key=lambda value: (value in (0, dimension - 1), value))
        return center_order

    def _iterate_coordinates(self, ranges: List[Iterable[int]]) -> Iterable[Coordinate]:
        for x in ranges[0]:
            for y in ranges[1]:
                for z in ranges[2]:
                    for w in ranges[3]:
                        yield (x, y, z, w)

    def _deploy_back_rank(self, owner: int, positions: Iterable[Coordinate], occupied: set[Coordinate]) -> None:
        sequence = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook, Cat, Alien]
        for piece_cls, position in zip(sequence, positions):
            if not within_bounds(position, self.board.shape):
                continue
            if position in occupied:
                continue
            piece = piece_cls(owner)
            self.board.place_piece(piece, position)
            occupied.add(position)
            if isinstance(piece, King):
                self._king_positions[owner] = position

    def _deploy_pawns(self, owner: int, positions: Iterable[Coordinate], occupied: set[Coordinate]) -> None:
        count = 0
        for position in positions:
            if not within_bounds(position, self.board.shape):
                continue
            if position in occupied:
                continue
            pawn = Pawn(owner)
            self.board.place_piece(pawn, position)
            occupied.add(position)
            count += 1
            if count >= self.board.shape[2] * self.board.shape[3] // 2:
                break

    # Gameplay ------------------------------------------------------------------
    def legal_moves_from(self, position: Coordinate) -> List[Move]:
        piece = self.board.get_piece(position)
        if piece is None:
            return []
        return piece.get_moves(self.board, position, self.rules)

    def legal_moves_for_player(self, player_id: int) -> List[Move]:
        moves: List[Move] = []
        for position, piece in self.board.iter_positions():
            if piece.owner != player_id:
                continue
            moves.extend(piece.get_moves(self.board, position, self.rules))
        return moves

    def execute_move(self, player_id: int, start: Coordinate, end: Coordinate, metadata: Optional[Dict[str, object]] = None) -> str:
        piece = self.board.get_piece(start)
        if piece is None:
            raise ValueError("No piece at the starting coordinate")
        if piece.owner != player_id:
            raise ValueError("Piece does not belong to the player")
        legal_moves = [move for move in piece.get_moves(self.board, start, self.rules) if move.end == end]
        if metadata:
            legal_moves = [move for move in legal_moves if move.metadata == metadata or all(item in move.metadata.items() for item in metadata.items())]
        if not legal_moves:
            raise ValueError("Illegal move")
        selected = legal_moves[0]
        if selected.move_type == "scratch":
            target_piece = self.board.get_piece(end)
            if target_piece is None or target_piece.owner == player_id:
                raise ValueError("Scratch requires an opposing piece")
            target_piece.mark_scratched()
            result = f"{piece.name} scratched {target_piece.name} at {coordinate_to_string(end)}"
        elif selected.move_type == "layout":
            self.board.apply_layout(piece, selected.metadata)
            self.rules = MovementRules(self.board.shape, self.pawn_profiles)
            result = f"{piece.name} executed {selected.metadata['operation']}"
        else:
            captured = self.board.move_piece(start, end)
            piece.has_moved = True
            result = f"{piece.name} moved to {coordinate_to_string(end)}"
            if captured:
                self._captured[player_id].append(captured.name)
                result += f" capturing {captured.name}"
                if isinstance(captured, King):
                    self._eliminate_player(captured.owner)
            if isinstance(piece, King):
                self._king_positions[player_id] = end
        self.next_turn()
        return result

    def perform_layout(self, player_id: int, metadata: Dict[str, object]) -> str:
        alien_position = self._find_alien(player_id)
        if alien_position is None:
            raise ValueError("Player does not control an Alien")
        alien_piece = self.board.get_piece(alien_position)
        assert alien_piece is not None
        layout_move = [move for move in alien_piece.get_moves(self.board, alien_position, self.rules) if move.move_type == "layout" and move.metadata["operation"] == metadata["operation"]]
        if not layout_move:
            raise ValueError("Invalid layout operation")
        self.board.apply_layout(alien_piece, metadata)
        self.rules = MovementRules(self.board.shape, self.pawn_profiles)
        self.next_turn()
        return f"Alien performed {metadata['operation']}"

    def _find_alien(self, player_id: int) -> Optional[Coordinate]:
        for position, piece in self.board.iter_positions():
            if piece.owner == player_id and isinstance(piece, Alien):
                return position
        return None

    def _eliminate_player(self, player_id: int) -> None:
        if player_id in self.active_players:
            self.active_players.remove(player_id)
        if player_id in self._king_positions:
            self._king_positions.pop(player_id, None)
        if len(self.active_players) == 1:
            self.turn_index = 0

    def winner(self) -> Optional[int]:
        if len(self.active_players) == 1:
            return self.active_players[0]
        return None

    # Serialization --------------------------------------------------------------
    def save(self, path: str) -> None:
        data = {
            "board": self.board.to_dict(),
            "players": [player.__dict__ for player in self.players],
            "turn_index": self.turn_index,
            "active_players": self.active_players,
            "captured": self._captured,
        }
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)

    @classmethod
    def load(cls, path: str) -> "GameEngine":
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        players = [Player(**player) for player in data["players"]]
        shape = tuple(data["board"]["shape"])
        engine = cls(shape, len(players))
        engine.players = players
        engine.board = Board.from_dict(data["board"], engine._piece_from_data)
        engine.turn_index = data["turn_index"]
        engine.active_players = data["active_players"]
        engine._captured = {int(k): v for k, v in data["captured"].items()}
        engine.rules = MovementRules(engine.board.shape, engine.pawn_profiles)
        engine._recalculate_kings()
        return engine

    def _piece_from_data(self, data: Dict[str, object]):
        piece_type = data["type"]
        owner = data["owner"]
        piece_map = {
            "King": King,
            "Queen": Queen,
            "Rook": Rook,
            "Bishop": Bishop,
            "Knight": Knight,
            "Pawn": Pawn,
            "Cat": Cat,
            "Alien": Alien,
        }
        cls = piece_map[piece_type]
        piece = cls(owner)
        piece.scratched = data.get("scratched", False)
        piece.has_moved = data.get("has_moved", False)
        if isinstance(piece, King):
            self._king_positions[owner] = tuple(data["position"])  # type: ignore[assignment]
        return piece

    def _recalculate_kings(self) -> None:
        self._king_positions.clear()
        for position, piece in self.board.iter_positions():
            if isinstance(piece, King):
                self._king_positions[piece.owner] = position

    # Debug utilities ------------------------------------------------------------
    def board_snapshot(self) -> List[str]:
        snapshot: List[str] = []
        for position, piece in self.board.iter_positions():
            snapshot.append(f"{piece.name}@{coordinate_to_string(position)}")
        return snapshot


__all__ = ["GameEngine", "Player"]
