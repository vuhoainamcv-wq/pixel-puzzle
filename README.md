# Pixel Puzzle League 🎨

Puzzle game inspired by *University War* (Pixel Painting).

## How to Play
- Choose **3 cards** out of 9.
- Cards may be rotated **mentally** (0/90/180/270), but you cannot rotate them in the UI.
- Stack the 3 cards to match the **Target** image.

## Color Rules
- Base: Red (R), Blue (B), Yellow (Y), Empty (N)
- Same colors stack: B + B → B
- Mix only in **1:1**:
  - R + B = Purple
  - R + Y = Orange
  - B + Y = Green
  - R + B + Y = Black
- Invalid: B + B + Y ❌

## Game Mode
- 5 rounds per run (Easy → Elite)
- Wrong answer: **+10s penalty**
- Top 5 fastest times saved locally

## Project Structure
- `generator/` → engine + solver + puzzle generator (Python)
- `web/` → playable UI (HTML/CSS/JS)

## Run
```bash
python generator/generate_banks.py
cd web
python -m http.server
