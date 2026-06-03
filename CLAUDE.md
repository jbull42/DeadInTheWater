# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the game

```bash
source venv/bin/activate
python main.py
```

Controls: arrow keys — Left/Right to turn, Up to accelerate, Down to brake.

## Architecture

Two source files, deliberately split between state and rendering:

- **`classes/ship.py`** — `Ship` owns all mutable state: `x`, `y`, `heading` (degrees), `speed`. `update(keys)` applies input and moves the ship each frame. Speed floors at 0 (no reverse).
- **`main.py`** — owns the pygame loop, event handling, and `draw_ship()` (a standalone function, not a Ship method). This keeps rendering logic out of the model.

Window: 800×600 at 60 fps. Background color `(15, 30, 60)` is the ocean.

## Dependencies

pygame 2.6.1, Python 3.11. The `venv/` directory is committed; no `requirements.txt` exists yet.
