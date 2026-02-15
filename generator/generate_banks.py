# generator/generate_banks.py
import json
from generator import generate_puzzle


BANKS = {
    "easy": dict(
        density=2,
        min_mixed=0,
        require_unique_solution=False,
        require_family_compat=False,
        require_center_clean=False,

        cheap_candidates=1200,
        solve_top_k=80,
        pick_mode="max_obv",  # easy = choose most obvious
    ),

    "normal": dict(
        density=3,
        min_mixed=1,
        require_unique_solution=True,
        require_family_compat=True,
        require_center_clean=False,

        cheap_candidates=1500,
        solve_top_k=100,
        pick_mode="min_obv",
    ),

    "hard": dict(
        density=3,
        min_mixed=2,
        require_unique_solution=True,
        require_family_compat=True,
        require_center_clean=False,

        cheap_candidates=1800,
        solve_top_k=120,
        pick_mode="min_obv",
    ),

    "expert": dict(
        density=4,
        min_mixed=2,
        require_unique_solution=True,
        require_family_compat=True,
        require_center_clean=True,   # chỉ expert+ mới clean center

        cheap_candidates=2200,
        solve_top_k=140,
        pick_mode="min_obv",
    ),

    "elite": dict(
        density=4,
        min_mixed=3,
        require_unique_solution=True,
        require_family_compat=True,
        require_center_clean=True,

        cheap_candidates=2600,
        solve_top_k=160,
        pick_mode="min_obv",
    ),
}


def generate_bank(name, count):
    print(f"Generating bank: {name} ({count} puzzles)")
    cfg = BANKS[name]
    puzzles = []

    for i in range(count):
        pz = generate_puzzle(
            density=cfg["density"],
            min_mixed=cfg["min_mixed"],
            max_black=1,
            require_center_white=True,

            require_unique_solution=cfg["require_unique_solution"],
            require_family_compat=cfg["require_family_compat"],
            require_center_clean=cfg["require_center_clean"],

            cheap_candidates=cfg["cheap_candidates"],
            solve_top_k=cfg["solve_top_k"],
            pick_mode=cfg["pick_mode"],
        )

        puzzles.append({
            "target": pz["target"],
            "cards": pz["cards"],
            # debug nếu cần:
            # "kill": pz["kill"],
            # "obviousness": round(pz["obviousness"], 2),
            # "num_solutions": pz["num_solutions"],
        })

        print(f"  ✓ {i+1}/{count}")

    return puzzles


def main():
    output = {}
    for bank in BANKS:
        output[bank] = generate_bank(bank, count=10)

    with open("web/puzzles.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print("\nDone! Saved to web/puzzles.json")


if __name__ == "__main__":
    main()
