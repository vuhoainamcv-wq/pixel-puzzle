# generator/engine.py
"""
Pixel Puzzle Engine (University War rules)

Symbols:
- N = empty
- R = red
- B = blue
- Y = yellow

Mixed results:
- P = purple (R+B)
- O = orange (R+Y)
- G = green  (B+Y)
- K = black  (R+B+Y)

Rules:
- Same colors can stack: B+B+N -> B
- Mixing only valid in 1:1 ratio:
    R+B -> P
    R+Y -> O
    B+Y -> G
    R+B+Y -> K
- Invalid: B+B+Y (2:1)
- Rotation allowed (0/90/180/270)
"""

from collections import Counter

# --- Bitmask encoding ---
C2B = {"N": 0, "R": 1, "B": 2, "Y": 4}

B2C = {
    0: "N",
    1: "R",
    2: "B",
    4: "Y",
    3: "P",  # R+B
    5: "O",  # R+Y
    6: "G",  # B+Y
    7: "K",  # R+B+Y
}


# =========================
# Rotation
# =========================
def rot90(mat):
    """
    Rotate 3x3 matrix 90 degrees clockwise.
    """
    return [[mat[2 - c][r] for c in range(3)] for r in range(3)]


def rotate(mat, k):
    """
    Rotate matrix by k * 90 degrees.
    k in {0,1,2,3}
    """
    out = mat
    for _ in range(k % 4):
        out = rot90(out)
    return out


# =========================
# Overlay rules
# =========================
def overlay_cell(values):
    """
    Overlay one cell from 3 cards.

    values: list of length 3, each in {"N","R","B","Y"}

    Returns:
      (result_symbol, valid_bool)
    """
    # Remove empty
    bits = [C2B[v] for v in values if v != "N"]

    # All empty
    if not bits:
        return "N", True

    cnt = Counter(bits)

    # Case 1: only one color repeated -> allowed
    if len(cnt) == 1:
        only = next(iter(cnt.keys()))
        return B2C[only], True

    # Case 2: multiple different colors exist
    # Valid only if each distinct color appears exactly once (1:1 ratio)
    if all(v == 1 for v in cnt.values()):
        mask = 0
        for b in cnt.keys():
            mask |= b
        return B2C[mask], True

    # Otherwise invalid ratio (e.g. B+B+Y)
    return "N", False


def overlay(cards3):
    """
    Overlay 3 full 3x3 cards.

    cards3: list of 3 matrices (3x3)

    Returns:
      (target_matrix, valid_bool)
    """
    target = [["N"] * 3 for _ in range(3)]
    ok = True

    for r in range(3):
        for c in range(3):
            cell, valid = overlay_cell(
                [cards3[0][r][c], cards3[1][r][c], cards3[2][r][c]]
            )
            if not valid:
                ok = False
            target[r][c] = cell

    return target, ok


# =========================
# Utility
# =========================
def print_grid(grid):
    """
    Pretty print 3x3 grid.
    """
    for row in grid:
        print(" ".join(row))
    print()
