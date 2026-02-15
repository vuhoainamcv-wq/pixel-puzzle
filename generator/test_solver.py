# generator/test_solver.py
from solver import solve_all, exists_solution_for_selection

# 9 dummy cards, but only first 3 matter here
cards = []

# Card 0: R at (0,0)
cards.append([
    ["R","N","N"],
    ["N","N","N"],
    ["N","N","N"],
])

# Card 1: B at (0,1)
cards.append([
    ["N","B","N"],
    ["N","N","N"],
    ["N","N","N"],
])

# Card 2: Y at (0,2)
cards.append([
    ["N","N","Y"],
    ["N","N","N"],
    ["N","N","N"],
])

# Fill remaining cards as all empty
for _ in range(6):
    cards.append([
        ["N","N","N"],
        ["N","N","N"],
        ["N","N","N"],
    ])

target = [
    ["R","B","Y"],
    ["N","N","N"],
    ["N","N","N"],
]

print("=== solve_all ===")
sols = solve_all(cards, target)
print("solutions:", sols)
print("count:", len(sols))

print("\n=== mental rotation check (selection [0,1,2]) ===")
ok, sol = exists_solution_for_selection(cards, target, [0,1,2])
print("exists?", ok, "solution:", sol)

print("\n=== mental rotation check (wrong selection [0,1,3]) ===")
ok, sol = exists_solution_for_selection(cards, target, [0,1,3])
print("exists?", ok, "solution:", sol)
