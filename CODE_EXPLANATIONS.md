# Number String Game — Code Explanations

This document explains every file in the project in plain language.
Read this before the defence so you can explain your code confidently.

---

## game_state.py

This is the most important file in the project. Every other file depends on it.
It defines the `GameState` class — the core data structure that represents a single
node in the game tree.

### `MOD6_MAP` and `mod6()`

```python
MOD6_MAP = {7: 1, 8: 2, 9: 3, 10: 4, 11: 5, 12: 6}

def mod6(n: int) -> tuple[int, bool]:
    if n > 6:
        return MOD6_MAP[n], True
    return n, False
```

This implements the substitution rule from the game description. When two numbers
are paired and their sum exceeds 6, you subtract 6 from the result (7→1, 8→2, etc.).

The function returns two things:
- The final value after substitution
- A boolean — `True` if substitution was used, `False` if not

The boolean is needed so the caller knows whether to increment the bank.

`MOD6_MAP` is a lookup table — instead of computing `n - 6` every time, we just
look up the answer directly. Both approaches are correct; the lookup table is
slightly faster.

---

### The `GameState` class

Every node in the game tree is a `GameState` object. It holds four things:

| Attribute | Type | Description |
|-----------|------|-------------|
| `nums`    | `list[int]` | The current number string — shrinks by 1 every move |
| `points`  | `int`       | Running total score (shared between both players) |
| `bank`    | `int`       | Increments whenever a substitution is used |
| `turn`    | `str`       | Whose turn it is — `'first'` or `'second'` |

---

### `clone()`

```python
def clone(self) -> GameState:
    return GameState(self.nums, self.points, self.bank, self.turn)
```

Creates an exact copy of the current state. Used by `apply_move()` to return a
new state without touching the original.

---

### `get_moves()`

```python
def get_moves(self) -> list[dict]:
```

Returns all legal moves for the current state. There are two types:

**Pair move** — one for each fixed slot:
```python
{'type': 'pair', 'pair_idx': 0}   # collapse positions (0, 1)
{'type': 'pair', 'pair_idx': 1}   # collapse positions (2, 3)
{'type': 'pair', 'pair_idx': 2}   # collapse positions (4, 5)
```

`pair_idx * 2` always lands on an even index — this enforces the fixed slot rule
and guarantees you can never pair across a slot boundary (e.g. positions 1 and 2).

**Delete move** — only available when two conditions are both true:
- The string length is odd (the last element has no partner)
- The length is greater than 1 (a terminal state must never return a delete move)

```python
{'type': 'delete'}
```

---

### `apply_move()`

```python
def apply_move(self, move: dict) -> GameState:
```

Applies a move and returns a **brand new** `GameState`. It never modifies the
original state — this is intentional and critical.

**Why return a new state instead of modifying the existing one?**

Minimax and Alpha-Beta explore many different branches of the game tree starting
from the same state. If you modified the state in place you would corrupt branches
you haven't explored yet and would need to "undo" moves — which is error-prone.
Returning a new state keeps every branch completely independent.

For a **pair move**:
1. Calculate the sum of the two values
2. Apply mod-6 substitution if the sum exceeds 6
3. Replace the first value with the result, remove the second value
4. Add 1 to points; add 1 to bank if substitution was used

For a **delete move**:
1. Remove the last element from the string
2. Subtract 1 from points

Either way, `turn` flips at the end (`'first'` → `'second'` or vice versa).

---

### `get_result()`

```python
def get_result(self) -> str | None:
```

Checks the win condition. Only meaningful when `is_terminal()` is `True`.

Looks at the **parity** (even or odd) of two things:
- The final number remaining in the string
- The total score (`points + bank`)

| Final number | Total score | Result |
|-------------|-------------|--------|
| Even        | Even        | First player wins |
| Odd         | Odd         | Second player wins |
| Even        | Odd         | Draw |
| Odd         | Even        | Draw |

Returns `None` if the game is not yet finished.

---

## minimax.py

Implements the Minimax algorithm — the computer's decision-making brain.

### How Minimax works

Minimax assumes both players play perfectly. The computer (as one player) tries
to **maximise** its score, while the opponent tries to **minimise** it.

The algorithm builds a game tree by simulating all possible moves from the current
state down to a certain depth, then picks the move that leads to the best outcome
assuming the opponent also plays optimally.

- `'first'` is always the **maximising** player
- `'second'` is always the **minimising** player

### `heuristic()`

```python
def heuristic(state: GameState) -> float:
```

Called when the search reaches its depth limit on a non-terminal state. Since we
haven't reached the end of the game, we estimate how good the position is.

The heuristic looks at:
- **Parity of total score** — even total favours first player (+4 or -4)
- **Parity of remaining numbers** — more even numbers suggests an even final result
- **Bank size** — larger bank shifts the total score, slightly favouring first
- **String length parity** — even length means no forced delete on the next turn

Positive values favour `'first'`, negative values favour `'second'`.

### `minimax()`

```python
def minimax(state: GameState, depth: int, is_max: bool, counter: dict[str, int]) -> float:
```

The recursive core of the algorithm.

**Base case** — if the state is terminal or depth reaches 0:
- Terminal win for first: return `+100 + depth`
- Terminal win for second: return `-(100 + depth)`
- Draw: return `0`
- Depth limit reached: return `heuristic(state)`

The `+ depth` in the terminal score rewards finding wins faster — a win in 2 moves
is better than a win in 6 moves.

**Recursive case:**
- Maximising player: loop over all moves, return the highest value child
- Minimising player: loop over all moves, return the lowest value child

`counter['nodes']` is incremented on every call so we can report how many nodes
were evaluated.

### `get_best_move()`

```python
def get_best_move(state: GameState, depth: int) -> dict[str, object]:
```

The entry point called by the UI. Loops over all legal moves, calls `minimax` on
each child state, and returns the move with the best score along with stats:

```python
{ 'move': dict, 'nodes': int, 'time_ms': float }
```

---

## alphabeta.py

Implements the same algorithm as Minimax but with **Alpha-Beta pruning** — an
optimisation that skips branches that cannot possibly affect the final result.

### How Alpha-Beta pruning works

During the search, we track two values:
- **Alpha** — the best score the maximising player can already guarantee
- **Beta** — the best score the minimising player can already guarantee

If at any point `beta <= alpha`, we stop exploring the current branch. This is
called a **cut-off**. The reasoning is:

- If the minimiser already has a move that gives a score ≤ alpha, the maximiser
  will never choose this branch — so there is no point exploring it further.
- The same logic applies in reverse for the maximiser.

### `alphabeta()`

```python
def alphabeta(state: GameState, depth: int, alpha: float, beta: float,
              is_max: bool, counter: dict[str, int]) -> float:
```

Identical to `minimax()` except:
- Takes `alpha` and `beta` as extra parameters
- After each child is evaluated, updates alpha or beta
- Breaks out of the loop early if `beta <= alpha`

### Key guarantee

**Alpha-Beta always returns the same move as Minimax at the same depth.**

It never changes the result — it only skips branches it can prove are irrelevant.
The benefit is fewer nodes evaluated, which means faster move selection. In
practice Alpha-Beta typically evaluates roughly the square root of the nodes
that Minimax would evaluate.

### `get_best_move()`

Identical interface to `minimax.get_best_move()` — same parameters, same return
format. This means the UI can swap between the two algorithms with a single
setting change.

```python
from src.minimax import get_best_move as minimax_best
from src.alphabeta import get_best_move as alphabeta_best
```

---

## experiments.py

Handles recording and exporting game statistics for the assignment report.

### `ExperimentTracker` class

A simple tracker that stores a list of completed games and can export them to CSV.

### `record()`

```python
def record(self, algo: str, depth: int, length: int, starter: str,
           result: str, nodes: int, move_times: list[float],
           points: int, bank: int) -> None:
```

Called once at the end of each game. Stores everything needed for the report:
- Which algorithm was used and at what depth
- Who started the game
- Who won
- How many nodes the computer evaluated
- The average time per move

### `summary()`

Returns win/loss/draw counts broken down by algorithm — useful for comparing
Minimax vs Alpha-Beta performance across 10 games each.

### `export_csv()`

Writes all recorded games to a CSV file that can be pasted directly into the
assignment report.

---

## Likely defence questions

**Why does `apply_move` return a new state instead of modifying the existing one?**
Because Minimax and Alpha-Beta explore many branches from the same state. Mutating
in place would corrupt the tree. Returning a new state keeps every branch independent.

**What is the heuristic for and why do we need it?**
The game tree for a string of 15–25 numbers is too large to explore fully. The
heuristic estimates how good a position is when we reach the depth limit, so the
algorithm can still make a reasonable decision without searching the entire tree.

**Why does Alpha-Beta always agree with Minimax?**
Because pruned branches are ones that provably cannot change the result. Alpha-Beta
never skips a branch that could lead to a better move — it only skips branches
where the outcome is already determined by what has been found elsewhere.

**What does the bank do to the win condition?**
The bank accumulates whenever a substitution is used during pairing. At the end of
the game it is added to the total points before checking the win condition. This
means players can influence the parity of the final score by choosing moves that
do or do not trigger substitutions.

**Why is `pair_idx * 2` always an even index?**
Because the pairs are fixed positional slots — (0,1), (2,3), (4,5) etc. Multiplying
the pair index by 2 always gives 0, 2, 4... which are even indices. This enforces
the rule that you can only pair elements within a slot, never across a boundary.
