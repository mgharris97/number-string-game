import time
from src.game_state import GameState

# ----------------------------------------------------------------------
# Heuristic evaluation function for non‑terminal states.
# This is called when the search reaches its depth limit.
#
# The heuristic returns a float: positive values favour the first player,
# negative values favour the second player.
#
# We designed this heuristic after experimenting with several features.
# Each feature is multiplied by a weight that I tuned manually.
# ----------------------------------------------------------------------
def heuristic(state: GameState) -> float:
    n: int = len(state.nums)
    total: int = state.points + state.bank   # total score at the end of the game (so far)
    score: float = 0.0

    # Feature 1: Parity of total score (points + bank)
    # Weight: 4.0 (highest)
    # Reason: The win condition directly checks whether total score is even or odd.
    # Even total helps the first player (since first player needs final_even AND total_even).
    # Odd total helps the second player (needs final_odd AND total_odd).
    # This is the strongest signal, so I gave it the largest weight.
    score += 4.0 if total % 2 == 0 else -4.0

    # Feature 2: Difference between even and odd numbers in the current string
    # Weight: 1.5
    # Reason: More even numbers make future sums more likely to be even.
    # This indirectly influences the parity of the final number.
    # It's a predictor, not a direct factor, so weight is moderate.
    even_count: int = sum(1 for x in state.nums if x % 2 == 0)
    odd_count: int = n - even_count
    score += (even_count - odd_count) * 1.5

    # Feature 3: Current bank value
    # Weight: 0.8
    # Reason: The bank is added to total score at the end. Each bank point
    # flips the parity of the total. However, bank points do not compound,
    # and their effect is linear. So I gave a low weight.
    score += state.bank * 0.8

    # Feature 4: Parity of string length (even vs odd)
    # Weight: 2.0
    # Reason: An even length means no forced delete on the next turn,
    # giving the current player more choices (all pairs, no delete).
    # An odd length forces a delete option, which can be disadvantageous.
    # This is meaningful but less decisive than total parity.
    score += 2.0 if n % 2 == 0 else -2.0

    return score


# ----------------------------------------------------------------------
# Minimax recursive search with depth limit.
#
# Parameters:
#   state: current GameState
#   depth: remaining depth to search (when 0, use heuristic)
#   is_max: True if current node is a maximizing node (first player's turn)
#   counter: mutable dict to count total nodes visited (for experiments)
#
# Returns a float value from the perspective of the FIRST player.
# Positive = good for first, negative = good for second.
# ----------------------------------------------------------------------
def minimax(state: GameState, depth: int, is_max: bool, counter: dict[str, int]) -> float:
    # Count this node for performance statistics
    counter['nodes'] += 1

    # Base case 1: terminal state (one number left)
    if state.is_terminal() or depth == 0:
        result = state.get_result()
        if result == 'first':
            # First player wins. We add a small bonus (+depth) to prefer
            # wins that happen sooner (shorter path). This encourages the AI
            # to win faster and avoid unnecessary moves.
            return 100 + depth
        if result == 'second':
            # Second player wins. Negative with depth bonus to prefer earlier losses?
            # Actually, here negative with +depth makes the value less negative
            # when depth is larger. That means losing later is slightly better.
            # We chose this to make the AI delay loss if it cannot avoid it.
            return -(100 + depth)
        if result == 'draw':
            return 0
        # If depth == 0 and not terminal, use heuristic
        return heuristic(state)

    # Recursive case: generate all legal moves
    moves = state.get_moves()

    if is_max:
        # Maximizing player (first player)
        best = float('-inf')
        for move in moves:
            child = state.apply_move(move)
            val = minimax(child, depth - 1, False, counter)
            best = max(best, val)
        return best
    else:
        # Minimizing player (second player)
        best = float('inf')
        for move in moves:
            child = state.apply_move(move)
            val = minimax(child, depth - 1, True, counter)
            best = min(best, val)
        return best


# ----------------------------------------------------------------------
# Public function to get the best move from the current state.
# It runs minimax for each possible move and picks the best according
# to whether the current player is first (max) or second (min).
#
# Returns a dictionary with:
#   'move'    : the best move (dict)
#   'nodes'   : total nodes visited during search
#   'time_ms' : elapsed time in milliseconds
# ----------------------------------------------------------------------
def get_best_move(state: GameState, depth: int) -> dict[str, object]:
    counter: dict[str, int] = {'nodes': 0}
    is_first: bool = state.turn == 'first'   # True if first player to move
    best_move: dict | None = None
    best_val: float = float('-inf') if is_first else float('inf')
    t0: float = time.time()

    # Try each legal move from the current state
    for move in state.get_moves():
        child = state.apply_move(move)
        # Call minimax on the child with reduced depth and opposite player
        val = minimax(child, depth - 1, not is_first, counter)

        # Update best move based on player type
        if is_first and val > best_val:
            best_val = val
            best_move = move
        elif not is_first and val < best_val:
            best_val = val
            best_move = move

    return {
        'move': best_move,
        'nodes': counter['nodes'],
        'time_ms': (time.time() - t0) * 1000,
    }


# NOTES

# 1. Why did we choose these heuristic weights?
#    - We ran a small tournament: AI vs Human with different weight sets.
#    - The weights shown gave the highest win rate against a simple baseline.
#    - We did not use machine learning; We tuned manually over ~20 games.
#
# 2. What is the effect of the `+ depth` bonus in terminal states?
#    - It makes the AI prefer winning in fewer moves (shorter path).
#    - For losses, it prefers losing later (less negative).
#    - This is a common trick to make the AI play more "naturally".
#
# 3. Why no alpha‑beta pruning in this version?
#    - We implemented alpha‑beta separately in `alphabeta.py`.
#    - This minimax version is kept clean for understanding and testing.
#    - In the final UI, We actually choose between alpha‑beta or Minimax.
#
# 4. How do I choose the depth?
#    - For human vs AI, We set depth up to 6 . This gives < 0.5 sec per move.
#    - Depth > 6 becomes too slow without pruning.
#
# 5. Example of how the heuristic works:
#    Suppose state: nums=[2,3,4], points=1, bank=0, length=3 (odd)
#    total=1 (odd) -> -4.0
#    evens=2 (2,4), odds=1 -> (2-1)*1.5 = +1.5
#    bank=0 -> 0
#    length odd -> -2.0
#    Total heuristic = -4.0 + 1.5 - 2.0 = -4.5 (favours second player)
#
# 6. Limitations we observed:
#    - The heuristic still ignores the exact value of the final number.
#    - It cannot foresee forced sequences that lead to a specific final parity.
#    - Against a perfect player, depth 5 is often not enough.
#
# 7. How we tested correctness:
#    - Unit tests for terminal states (return 100+depth, etc.)
#    - Verified that get_best_move returns a legal move.
#    - Compared values with a brute‑force search for small strings (length <= 5).
