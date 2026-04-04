# Number String Game

A deterministic two-player game with perfect information, where a human plays against a computer. The computer uses either the **Minimax** or **Alpha-Beta pruning** algorithm to select its moves.

Built with Python and Tkinter

---

## Team members

| Name | Role |
|------|------|
| Rithweek | Game logic (`src/game_state.py`) |
| Nizzah | Minimax algorithm (`src/minimax.py`) |
| Matthew | Alpha-Beta algorithm (`src/alphabeta.py`) |
| Ilham | Tests (`tests/`) |
| Omar | Experiments & stats (`src/experiments.py`), UI (`src/ui.py`) |

---

## Game rules

At the start of the game a string of numbers is randomly generated. The length is chosen by the human player and must be between 15 and 25. Each number in the string is in the range 1–6.

Players take turns. On each turn a player must do exactly one of the following:

**Pair** — choose one of the fixed adjacent pairs (1st+2nd, 3rd+4th, 5th+6th, etc.) and replace the two numbers with their sum. If the sum exceeds 6, a substitution is applied (7→1, 8→2, 9→3, 10→4, 11→5, 12→6). Pairing adds 1 point to the total score. If a substitution was used, 1 point is also added to the bank.

**Delete** — only available when the string has an odd number of elements. Removes the last unpaired number and subtracts 1 point from the total score.

Every move reduces the string length by exactly 1. The game ends when one number remains.

**Winning condition** — at the end, the bank is added to the total score:
- Final number even AND total score even → the first player wins
- Final number odd AND total score odd → the second player wins
- Otherwise → draw

---

## Project structure

```
number-string-game/
├── LICENSE
├── README.md
├── requirements.txt
├── main.py                  # entry point
├── src
│   ├── alphabeta.py         # Alpha-Beta pruning algorithm
│   ├── experiments.py       # stats tracking and CSV export
│   ├── game_state.py        # GameState class, move generation, win detection
│   ├── minimax.py           # Minimax algorithm and heuristic evaluation
│   └── ui.py                # Tkinter graphical interface
├── team-brief-1.md
├── tests
│   ├── test_algorithms.py   # tests for game logic
│   └── test_game_state.py   # tests for Minimax and Alpha-Beta
└── venv

```

---

## How to run
 
**Requirements:** Python 3.10 or higher. Tkinter is included with standard Python installations.
 
Clone the repository and set up the environment:
 
```bash
git clone https://github.com/YOUR_USERNAME/number-string-game.git
cd number-string-game
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
 
Run the game:
 
```bash
python main.py
```
 
Run the tests:
 
```bash
python -m pytest tests/ -v
```
 
---
 
## Git workflow
 
Each team member works on their own branch and then just merges to the main branch to avoid having to do pull requests
 
**Branches:**
 
| Name | Role |
|------|------|
| Rithweek | Game logic (`src/game_state.py`) |
| Nizzah | Minimax algorithm (`src/minimax.py`) |
| Matthew | Alpha-Beta algorithm (`src/alphabeta.py`) |
| Ilham | Tests (`tests/`) |
| Omar | Experiments & stats (`src/experiments.py`), UI (`src/ui.py`) |

**Setup — do this once after cloning:**
 
```bash
git checkout -b your-branch-name
```
For example, I'd run ```git checkout -b alphabeta```
 
**Daily workflow:**
 
```bash
git add .
git commit -m "describe what you did"
git push -u origin your-branch-name
```
 
**Staying up to date** — whenever you come to work on the project, pull changes from `main`
 
```bash
git checkout main
git pull
git checkout your-branch-name
git merge main
```

**When your work is ready** — let the team know and one of us will merge your branch into `main` on GitHub.
 
> Never push directly to `main` — always push to your own branch since two pushes at the same time will create conflicts
---

## Algorithms

The computer player supports two search algorithms, both implemented as N-ply lookahead:

**Minimax** — explores the full game tree up to the configured depth, assuming both players play optimally.

**Alpha-Beta pruning** — produces identical results to Minimax but prunes branches that cannot affect the outcome, evaluating significantly fewer nodes.

The search depth (3–6 plies) and starting player are configurable before each game.# number-string-game
