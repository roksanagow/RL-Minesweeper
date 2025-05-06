# backend/utils.py

import random
from typing import List, Tuple


def generate_random_positions(width: int, height: int, count: int, exclude: Tuple[int, int] = None, seed: int = None) -> List[Tuple[int, int]]:
    """
    Generate a list of unique (row, col) positions.
    Optionally exclude a coordinate (e.g., for safe first click).
    """
    all_coords = [(r, c) for r in range(height) for c in range(width)]
    if exclude and exclude in all_coords:
        all_coords.remove(exclude)

    if seed is not None:
        random.seed(seed)

    return random.sample(all_coords, count)


def get_neighbors(row: int, col: int, width: int, height: int) -> List[Tuple[int, int]]:
    """
    Return a list of valid neighboring coordinates (8-way) for (row, col).
    """
    neighbors = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            nr, nc = row + dr, col + dc
            if (dr != 0 or dc != 0) and 0 <= nr < height and 0 <= nc < width:
                neighbors.append((nr, nc))
    return neighbors


def print_board_debug(board: List[List[int]], revealed: List[List[bool]] = None, flags: List[List[bool]] = None):
    """
    Print the board for debugging purposes.
    Shows revealed tiles, flags, and mines/numbers.
    """
    for r in range(len(board)):
        row_str = ""
        for c in range(len(board[0])):
            if flags and flags[r][c]:
                row_str += " F "
            elif revealed and not revealed[r][c]:
                row_str += " . "
            elif board[r][c] == -1:
                row_str += " * "
            else:
                row_str += f" {board[r][c]} "
        print(row_str)


def serialize_board(board: List[List[int]]) -> List[List[int]]:
    """
    Convert a board (e.g., internal state) to a JSON-safe list of lists.
    """
    return [row[:] for row in board]


def deep_copy_board(board: List[List[int]]) -> List[List[int]]:
    """
    Deep copy a 2D list of the board state.
    """
    return [row[:] for row in board]
