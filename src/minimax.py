import time
from src.game_state import GameState


# Evaluate a non-terminal state; positive favours 'first', negative favours 'second'
# Called when the search reaches its depth limit
def heuristic(state: GameState) -> float:
    n:           int   = len(state.nums)
    total:       int   = state.points + state.bank
    score:       float = 0.0

    # Weight: 4.0 — highest weight because the win condition directly checks
    # whether the total score is even or odd, making this the strongest signal.
    score += 4.0 if total % 2 == 0 else -4.0

    # Weight: 1.5 — more even numbers make future sums more likely to be even,
    # indirectly influencing the final number's parity. Moderate weight because
    # it is a predictor, not a direct factor in the win condition.
    even_count:  int   = sum(1 for x in state.nums if x % 2 == 0)
    odd_count:   int   = n - even_count
    score += (even_count - odd_count) * 1.5

    # Weight: 0.8 — the bank is added to points at game end, so each extra
    # bank point shifts the total by 1. Low weight because one point only
    # flips parity, it does not compound.
    score += state.bank * 0.8

    # Weight: 2.0 — even string length means no forced delete on the next
    # turn, giving the current player more choice. Meaningful but less
    # decisive than the total score parity itself.
    score += 2.0 if n % 2 == 0 else -2.0

    return score


# Minimax with N-ply lookahead; is_max=True when 'first' player is choosing
# counter is a mutable dict incremented on every recursive call to track total nodes visited
def minimax(state: GameState, depth: int, is_max:  bool, counter: dict[str, int]) -> float:
    counter['nodes'] += 1

    # Base case — terminal state or depth limit reached
    if state.is_terminal() or depth == 0:
        result = state.get_result()
        if result == 'first':  
            return  100 + depth
        if result == 'second': 
            return -(100 + depth)
        if result == 'draw':   
            return  0
        return heuristic(state)

    moves = state.get_moves()
#Maximising Player
    if is_max:
        best: float = float('-inf')
        #try each move, apply it, and repeatedly evaluate the child state
        for move in moves:
            val  = minimax(state.apply_move(move), depth - 1, False, counter)
            best = max(best, val)
        return best
 #Minimising Player       
    else:
        best: float = float('inf')
        for move in moves:
            val  = minimax(state.apply_move(move), depth - 1, True, counter)
            best = min(best, val)
        return best


# Find the best move for the current player using Minimax;
# returns a dict with keys: move (best move found), nodes (total evaluated), time_ms (elapsed)
def get_best_move(
    state: GameState,
    depth: int,
) -> dict[str, object]:
    counter:   dict[str, int]  = {'nodes': 0}
    is_first:  bool            = state.turn == 'first'
    best_move: dict | None     = None
    best_val:  float           = float('-inf') if is_first else float('inf')
    t0:        float           = time.time()

    for move in state.get_moves():
        child = state.apply_move(move)
        val   = minimax(child, depth - 1, not is_first, counter)

        if is_first and val > best_val:
            best_val  = val
            best_move = move
        elif not is_first and val < best_val:
            best_val  = val
            best_move = move

    return {
        'move':    best_move,
        'nodes':   counter['nodes'],
        'time_ms': (time.time() - t0) * 1000,
    }
