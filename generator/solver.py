# generator/solver.py
import itertools
from typing import List, Dict, Any, Tuple

from engine import rotate, overlay

Grid = List[List[str]]  # 3x3


def grids_equal(a: Grid, b: Grid) -> bool:
    for r in range(3):
        for c in range(3):
            if a[r][c] != b[r][c]:
                return False
    return True


def solve_all(cards: List[Grid], target: Grid) -> List[Dict[str, Any]]:
    """
    Find all solutions:
      - choose 3 cards out of len(cards)
      - choose rotations (0..3) for each of the 3 cards
      - overlay must be valid AND equal to target

    Returns list of solutions:
      {"cards": [i,j,k], "rots": [r1,r2,r3]}
    """
    sols = []
    n = len(cards)
    for comb in itertools.combinations(range(n), 3):
        for rots in itertools.product([0, 1, 2, 3], repeat=3):
            mats = [rotate(cards[comb[i]], rots[i]) for i in range(3)]
            out, ok = overlay(mats)
            if ok and grids_equal(out, target):
                sols.append({"cards": list(comb), "rots": list(rots)})
    return sols


def exists_solution_for_selection(cards: List[Grid], target: Grid, selection3: List[int]) -> Tuple[bool, Dict[str, Any] | None]:
    """
    Mental-rotation check:
    Given selected 3 card indices, does there exist rotations that match target?

    Returns:
      (True, solution_dict) if exists
      (False, None) otherwise
    """
    if len(selection3) != 3:
        raise ValueError("selection3 must have exactly 3 indices")

    for rots in itertools.product([0, 1, 2, 3], repeat=3):
        mats = [rotate(cards[selection3[i]], rots[i]) for i in range(3)]
        out, ok = overlay(mats)
        if ok and grids_equal(out, target):
            return True, {"cards": list(selection3), "rots": list(rots)}
    return False, None
