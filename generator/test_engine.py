# generator/test_engine.py

from engine import overlay_cell, overlay, rotate, print_grid

print("=== TEST overlay_cell ===")

# Same color stacking
print("B B N ->", overlay_cell(["B", "B", "N"]))  # should be ("B", True)

# Valid mixing
print("R B N ->", overlay_cell(["R", "B", "N"]))  # should be ("P", True)

# Invalid ratio
print("B B Y ->", overlay_cell(["B", "B", "Y"]))  # should be invalid

print("\n=== TEST rotation ===")

card = [
    ["R", "N", "N"],
    ["N", "B", "N"],
    ["N", "N", "Y"],
]

print("Original:")
print_grid(card)

print("Rotate 90:")
print_grid(rotate(card, 1))

print("Rotate 180:")
print_grid(rotate(card, 2))

print("\n=== TEST overlay full ===")

c1 = [
    ["R", "N", "N"],
    ["N", "N", "N"],
    ["N", "N", "N"],
]

c2 = [
    ["N", "B", "N"],
    ["N", "N", "N"],
    ["N", "N", "N"],
]

c3 = [
    ["N", "N", "Y"],
    ["N", "N", "N"],
    ["N", "N", "N"],
]

target, ok = overlay([c1, c2, c3])

print("Overlay result:")
print_grid(target)

print("Valid overlay?", ok)
