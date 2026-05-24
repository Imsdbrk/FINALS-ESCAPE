# Finals Escape: Aussie Student Survival

Finals Escape is a Python pygame game about surviving final exam week as an international student in Australia. The player balances energy, stress, money, and knowledge through daily choices, random events, and turn-based battles.

Current gameplay loop (battle-first):
- Choose one daily action.
- Resolve an automatic story event and stat change.
- Fight one action-specific enemy every day.
- Win to earn an item for future battles, or lose and take a stat penalty.

## Run Instructions

1. Install dependency:
```bash
python3 -m pip install pygame
```
2. Start the game:
```bash
python3 main.py
```
3. Main entry script:
`main.py`

## Tutor Notes (For COMP9001 Submission)

- External library used: `pygame` (not part of Python built-in library)
- Graphics/GUI used: Yes (`pygame` window rendering)
- Audio/video processing: No
- Web/network features: No
- Ed may not support GUI windows. Please run locally on laptop/desktop.

## Project Structure

- `main.py`: entry point to run the game
- `pygame_app.py`: pygame interface layer
- `engine.py`: game logic layer
- `content.py`: game data/configuration layer
- `models.py`: data classes
- `storage.py`: save/load JSON
- `pixel_assets/`: image assets used by pygame
- `make_pixel_assets.py`: optional script to regenerate local assets

The game is designed with low coupling: gameplay rules live in `engine.py` and configurable narrative/balance data lives in `content.py`.
