# Number String Game — Team Briefs

---

## Phase 1 — Core Logic

---

### Rithweek — Game State & Move Generation
**File:** `src/game_state.py`
**Priority:** Push stub first — everyone else is blocked until this exists.

#### Step 1 — Push this stub immediately
```python
class GameState:
    def __init__(self, nums, points=0, bank=0, turn='first'):
        self.nums   = list(nums)
        self.points = points
        self.bank   = bank
        self.turn   = turn

    def clone(self):
        return GameState(self.nums, self.points, self.bank, self.turn)

    def is_terminal(self):
        return len(self.nums) == 1

    def get_moves(self):
        raise NotImplementedError

    def apply_move(self, move):
        raise NotImplementedError

    def get_result(self):
        raise NotImplementedError
```

#### Step 2 — Full implementation
- `get_moves()` — returns a list of all legal moves:
  - `{'type': 'pair', 'pair_idx': int}` for each fixed slot (0+1, 2+3, 4+5 …)
  - `{'type': 'delete'}` only when `len(nums)` is odd
- `apply_move(move)` — returns a **new** `GameState`, never mutates in place:
  - Pair: replace two values with their sum; if sum > 6 apply mod-6 substitution (7→1 … 12→6); `points += 1`; if substitution used `bank += 1`
  - Delete: remove last element; `points -= 1`
  - Flip `turn` after every move
- `is_terminal()` — `True` when only 1 number remains
- `get_result()` — returns `'first'`, `'second'`, or `'draw'`:
  - Final number even AND `points + bank` even → `'first'` wins
  - Final number odd AND `points + bank` odd → `'second'` wins
  - Otherwise → `'draw'`

---

### Nizzah — Minimax Algorithm
**File:** `src/minimax.py`
**Priority:** Start against Rithweek's stub, swap in full implementation when ready.

#### What to build
- `heuristic(state)` — evaluation function for non-terminal states at depth cutoff:
  - Positive values favour `'first'`, negative favour `'second'`
  - Suggestions: parity of `points + bank`, parity of remaining numbers, number of available pairs
- `minimax(state, depth, is_max, counter)` — recursive Minimax:
  - Increment `counter['nodes']` on every call
  - Base case: terminal state or `depth == 0` → return score
  - `'first'` is always the maximising player, `'second'` always minimising
  - Terminal scores: `+100 + depth` for first win, `-(100 + depth)` for second win, `0` for draw
- `get_best_move(state, depth)` — iterates over all legal moves, returns:
  ```python
  { 'move': move, 'nodes': int, 'time_ms': float }
  ```

---

### Matthew — Alpha-Beta Pruning
**File:** `src/alphabeta.py`
**Priority:** Start alongside Nizzah — import her heuristic once she pushes it.

#### What to build
- `alphabeta(state, depth, alpha, beta, is_max, counter)` — recursive Alpha-Beta:
  - Same node counter and base cases as Minimax
  - Prune when `beta <= alpha`
- `get_best_move(state, depth)` — identical signature to Nizzah's, returns:
  ```python
  { 'move': move, 'nodes': int, 'time_ms': float }
  ```
- Import `heuristic` from `minimax.py` — do not rewrite it

#### Sanity check before merging
```python
from src.minimax import get_best_move as mm
from src.alphabeta import get_best_move as ab

result_mm = mm(state, depth=4)
result_ab = ab(state, depth=4)
assert result_mm['move'] == result_ab['move'], "Algorithms disagree!"
print(f"Minimax: {result_mm['nodes']} nodes | Alpha-Beta: {result_ab['nodes']} nodes")
```
Alpha-Beta should always produce the same move but with significantly fewer nodes.

---

### Teammate 5 — Experiment Tracker
**File:** `src/experiments.py`
**Priority:** Can start once `game_state.py` stub is up — does not need the algorithms yet.

#### What to build
`ExperimentTracker` class:
- `record(algo, depth, length, starter, result, nodes, move_times)` — saves one completed game
- `average_time(move_times)` — returns average move time in ms
- `summary()` — returns dict of win/loss/draw counts per algorithm
- `export_csv(filepath)` — writes all recorded games to CSV with columns:
  `Game, Algorithm, Depth, Length, Starter, Result, Nodes, AvgMs, Points, Bank`

```python
# Example usage
tracker = ExperimentTracker()
tracker.record(
    algo='alphabeta',
    depth=4,
    length=16,
    starter='human',
    result='first',
    nodes=1243,
    move_times=[120.3, 98.7, 134.2]
)
tracker.export_csv('results.csv')
```

---

### Ilham — Tests
**File:** `tests/`
**Priority:** Start once Rithweek's stub is up. Expand tests as each file is completed.

#### What to build

**`tests/test_game_state.py`**
```python
# Does apply_move shrink the string by 1?
# Does mod-6 substitution work correctly? (e.g. 4+5=9 → 3)
# Is delete only available when length is odd?
# Does get_result return the correct winner?
# Does apply_move never mutate the original state?
```

**`tests/test_minimax.py`**
```python
# Does get_best_move return a valid move?
# Does node count increase with depth?
# Does it pick an obvious winning move in a near-terminal state?
```

**`tests/test_alphabeta.py`**
```python
# Does Alpha-Beta always return the same move as Minimax at equal depth?
# Does Alpha-Beta always generate fewer or equal nodes than Minimax?
```

Run tests with:
```bash
python -m pytest tests/
```

---

## Phase 2 — UI (all 5 together, after Phase 1 is merged)

Once all Phase 1 files are merged into `main`, the team splits `src/ui.py`:

| Person | UI section |
|--------|-----------|
| Rithweek | Setup screen (length input, dropdowns, start button) |
| Nizzah | Number string display (pair slots, colour coding) |
| Matthew | Move buttons (pair buttons, delete button, status bar) |
| Ilham | Scoreboard + move log |
| Teammate 5 | Experiments tab + CSV export button |

More detail on each UI section will be added here once Phase 1 is complete.

