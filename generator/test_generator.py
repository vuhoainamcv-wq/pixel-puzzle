# generator/test_generator.py

from generator import generate_puzzle
from engine import print_grid

print("Generating one puzzle...")

pz = generate_puzzle(
    density=3,
    min_mixed=2,
    max_black=1,
    require_center_white=True,
)

print("\n=== TARGET ===")
print_grid(pz["target"])

print("Solution:", pz["solution"])
