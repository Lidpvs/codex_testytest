"""Command line interface for the 4D chess game."""
from __future__ import annotations

import argparse
from typing import List

from game.engine import GameEngine
from game.rules import Move, coordinate_to_string


def parse_coordinate(text: str):
    text = text.strip().replace("(", "").replace(")", "")
    parts = [p.strip() for p in text.split(",") if p.strip()]
    if len(parts) != 4:
        raise ValueError("Coordinates must contain four integers")
    return tuple(int(value) for value in parts)


def describe_moves(moves: List[Move]) -> List[str]:
    descriptions: List[str] = []
    for move in moves:
        descriptions.append(f"{move.move_type.upper()}: {move.describe()}")
    return descriptions


def repl(engine: GameEngine) -> None:
    print("Welcome to 4D Chess! Type 'help' for commands.")
    while True:
        player = engine.current_player_id
        command = input(f"[{engine.players[player].name}] > ").strip()
        if not command:
            continue
        if command in {"quit", "exit"}:
            print("Goodbye!")
            break
        if command == "help":
            print("Commands: board, moves <coord>, move <start> <end>, layout <op> <params>, save <path>, load <path>, winner, quit")
            continue
        if command == "board":
            for entry in engine.board_snapshot():
                print(entry)
            continue
        if command.startswith("moves"):
            try:
                _, coord_text = command.split(maxsplit=1)
                coord = parse_coordinate(coord_text)
                moves = engine.legal_moves_from(coord)
                if not moves:
                    print("No legal moves for that square.")
                else:
                    for line in describe_moves(moves):
                        print(line)
            except ValueError as exc:
                print(exc)
            continue
        if command.startswith("move"):
            try:
                _, start_text, end_text = command.split(maxsplit=2)
                start = parse_coordinate(start_text)
                end = parse_coordinate(end_text)
                result = engine.execute_move(player, start, end)
                print(result)
            except ValueError as exc:
                print(f"Error: {exc}")
            continue
        if command.startswith("layout"):
            parts = command.split()
            if len(parts) < 2:
                print("Usage: layout <operation> ...")
                continue
            operation = parts[1]
            try:
                metadata = parse_layout(operation, parts[2:])
                metadata["operation"] = operation
                message = engine.perform_layout(player, metadata)
                print(message)
            except ValueError as exc:
                print(f"Error: {exc}")
            continue
        if command.startswith("save"):
            try:
                _, path = command.split(maxsplit=1)
                engine.save(path)
                print(f"Game saved to {path}")
            except ValueError as exc:
                print(exc)
            continue
        if command.startswith("load"):
            try:
                _, path = command.split(maxsplit=1)
                new_engine = GameEngine.load(path)
                engine.board = new_engine.board
                engine.players = new_engine.players
                engine.turn_index = new_engine.turn_index
                engine.active_players = new_engine.active_players
                engine.pawn_profiles = new_engine.pawn_profiles
                engine.rules = new_engine.rules
                print(f"Loaded game from {path}")
            except ValueError as exc:
                print(exc)
            continue
        if command == "winner":
            winner = engine.winner()
            if winner is None:
                print("No winner yet.")
            else:
                print(f"Winner: {engine.players[winner].name}")
            continue
        print("Unknown command. Type 'help' for assistance.")


def parse_layout(operation: str, params: List[str]):
    if operation == "transpose":
        if len(params) != 4:
            raise ValueError("Transpose requires four axis indices")
        axes = tuple(int(p) for p in params)
        return {"axes": axes}
    if operation == "swap_axis":
        if len(params) != 2:
            raise ValueError("swap_axis requires two axis indices")
        return {"axes": (int(params[0]), int(params[1]))}
    if operation == "move_axis":
        if len(params) != 2:
            raise ValueError("move_axis requires source and destination indices")
        return {"source": int(params[0]), "destination": int(params[1])}
    if operation == "reshape_axis":
        if len(params) != 6:
            raise ValueError("reshape_axis requires axis pair followed by four dimensions")
        axis_pair = (int(params[0]), int(params[1]))
        new_shape = tuple(int(p) for p in params[2:6])
        return {"axis_pair": axis_pair, "new_shape": new_shape}
    raise ValueError(f"Unknown layout operation {operation}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Play four-dimensional chess.")
    parser.add_argument("--players", type=int, default=2, help="Number of players (2-4)")
    parser.add_argument("--shape", nargs=4, type=int, default=(4, 4, 4, 4), help="Board dimensions")
    args = parser.parse_args()
    engine = GameEngine(tuple(args.shape), args.players)
    repl(engine)


if __name__ == "__main__":
    main()
