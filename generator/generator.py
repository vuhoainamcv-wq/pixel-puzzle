# generator/generator.py
import random
from collections import Counter

from engine import overlay, rotate
from solver import solve_all


RED_FAMILY = {"R", "P", "O", "K"}
BLUE_FAMILY = {"B", "P", "G", "K"}
YELLOW_FAMILY = {"Y", "O", "G", "K"}

MIXED = {"P", "O", "G", "K"}


def random_card(density=3):
    mat = [["N"] * 3 for _ in range(3)]
    coords = [(r, c) for r in range(3) for c in range(3)]
    random.shuffle(coords)

    density = max(0, min(int(density), 9))
    for i in range(density):
        r, c = coords[i]
        mat[r][c] = random.choice(["R", "B", "Y"])
    return mat


def count_mixed(target):
    return sum(1 for r in range(3) for c in range(3) if target[r][c] in MIXED)


def count_black(target):
    return sum(1 for r in range(3) for c in range(3) if target[r][c] == "K")


def center_white(target):
    return target[1][1] == "N"


def target_families(target):
    flat = [target[r][c] for r in range(3) for c in range(3)]
    red = any(x in RED_FAMILY for x in flat)
    blue = any(x in BLUE_FAMILY for x in flat)
    yellow = any(x in YELLOW_FAMILY for x in flat)
    return red, blue, yellow


def enforce_family_compat(cards, target):
    red_t, blue_t, yellow_t = target_families(target)

    if not red_t:
        if any(cards[k][r][c] == "R" for k in range(9) for r in range(3) for c in range(3)):
            return False
    if not blue_t:
        if any(cards[k][r][c] == "B" for k in range(9) for r in range(3) for c in range(3)):
            return False
    if not yellow_t:
        if any(cards[k][r][c] == "Y" for k in range(9) for r in range(3) for c in range(3)):
            return False
    return True


def enforce_center_clean_if_center_white(cards, target):
    if target[1][1] == "N":
        return all(cards[k][1][1] == "N" for k in range(9))
    return True


def one_step_kill_count(cards, target):
    """
    Softer: count cards that contradict target on N cells only (strong rule).
    This avoids over-filtering.
    """
    kill = 0
    for k in range(9):
        bad = 0
        for r in range(3):
            for c in range(3):
                if target[r][c] == "N" and cards[k][r][c] != "N":
                    bad += 1
        if bad >= 1:
            kill += 1
    return kill


def obviousness_score(cards, target):
    """
    Softer heuristic:
    - penalize leakage on N cells
    - penalize family leakage
    - mild distribution skew
    """
    score = 0.0

    # A) leakage on N cells (linear + mild quadratic)
    for r in range(3):
        for c in range(3):
            if target[r][c] == "N":
                colored = sum(1 for k in range(9) if cards[k][r][c] != "N")
                score += colored * 1.5 + (colored ** 2) * 0.3

    # B) family leakage (keep)
    red_t, blue_t, yellow_t = target_families(target)
    if not red_t:
        score += sum(
            1 for k in range(9)
            if any(cards[k][r][c] == "R" for r in range(3) for c in range(3))
        ) * 4.0
    if not blue_t:
        score += sum(
            1 for k in range(9)
            if any(cards[k][r][c] == "B" for r in range(3) for c in range(3))
        ) * 4.0
    if not yellow_t:
        score += sum(
            1 for k in range(9)
            if any(cards[k][r][c] == "Y" for r in range(3) for c in range(3))
        ) * 4.0

    # C) mild skew
    for r in range(3):
        for c in range(3):
            cnt = Counter(cards[k][r][c] for k in range(9))
            top = max(cnt.values())
            score += max(0, top - 7) * 0.8

    return score


def make_candidate(density, min_mixed, max_black, require_center_white=True):
    cards = [random_card(density) for _ in range(9)]

    sol_cards = random.sample(range(9), 3)
    sol_rots = [random.choice([0, 1, 2, 3]) for _ in range(3)]
    mats = [rotate(cards[sol_cards[i]], sol_rots[i]) for i in range(3)]
    target, ok = overlay(mats)
    if not ok:
        return None

    if require_center_white and not center_white(target):
        return None
    if count_black(target) > max_black:
        return None
    if count_mixed(target) < min_mixed:
        return None

    return cards, target


def generate_puzzle(
    density=3,
    min_mixed=0,
    max_black=1,
    require_center_white=True,

    require_unique_solution=True,
    require_family_compat=False,
    require_center_clean=False,

    # 2-phase controls
    cheap_candidates=2000,
    solve_top_k=120,
    max_rounds=15,

    # "min_obv" for hard, "max_obv" for easy
    pick_mode="min_obv",
):
    """
    Guaranteed-ish generator:
    - Phase 1: collect candidates that pass ONLY core constraints (no kill/obv filtering)
    - Phase 2: rank by kill/obv and solve only top-K until found.
    """

    for _round in range(max_rounds):
        pool = []

        for _ in range(cheap_candidates):
            out = make_candidate(
                density=density,
                min_mixed=min_mixed,
                max_black=max_black,
                require_center_white=require_center_white,
            )
            if out is None:
                continue

            cards, target = out

            if require_family_compat and not enforce_family_compat(cards, target):
                continue
            if require_center_clean and not enforce_center_clean_if_center_white(cards, target):
                continue

            kill = one_step_kill_count(cards, target)
            obv = obviousness_score(cards, target)

            pool.append({
                "cards": cards,
                "target": target,
                "kill": kill,
                "obviousness": obv,
            })

        if not pool:
            continue

        # Rank
        if pick_mode == "max_obv":
            pool.sort(key=lambda x: (x["obviousness"], x["kill"]), reverse=True)
        else:
            pool.sort(key=lambda x: (x["obviousness"], x["kill"]))

        # Solve top-K
        for cand in pool[: max(1, solve_top_k)]:
            sols = solve_all(cand["cards"], cand["target"])
            if require_unique_solution:
                if len(sols) != 1:
                    continue
            else:
                if len(sols) == 0:
                    continue

            return {
                "cards": cand["cards"],
                "target": cand["target"],
                "solution": sols[0] if sols else None,
                "num_solutions": len(sols),
                "kill": cand["kill"],
                "obviousness": cand["obviousness"],
            }

    raise RuntimeError("Failed to generate puzzle. Increase cheap_candidates/solve_top_k, or relax unique/center_clean.")
