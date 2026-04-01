import time
from src.game_state import GameState


def heuristic(state: GameState) -> float:
    """
    Evaluate a non-terminal state.

    Positive values favour 'first', negative values favour 'second'.
    Called when the search reaches its depth limit.

    Parameters
    ----------
    state : current game state to evaluate

    Returns
    -------
    float : heuristic score
    """
    n:           int   = len(state.nums)
    total:       int   = state.points + state.bank
    score:       float = 0.0

    # Parity of running total — even total favours first player
    score += 4.0 if total % 2 == 0 else -4.0

    # Parity bias of remaining numbers
    even_count:  int   = sum(1 for x in state.nums if x % 2 == 0)
    odd_count:   int   = n - even_count
    score += (even_count - odd_count) * 1.5

    # Bank adds to total score — more bank slightly favours first
    score += state.bank * 0.8

    # Even length means no forced delete next turn — slightly more control
    score += 2.0 if n % 2 == 0 else -2.0

    return score


def minimax(
    state:   GameState,
    depth:   int,
    is_max:  bool,
    counter: dict[str, int],
) -> float:
    """
    Minimax algorithm with N-ply lookahead.

    Parameters
    ----------
    state   : current game state
    depth   : plies remaining
    is_max  : True if the current player is maximising ('first')
    counter : mutable node counter — incremented on every call

    Returns
    -------
    float : evaluated score of the state
    """
    counter['nodes'] += 1

    # Base case — terminal state or depth limit reached
    if state.is_terminal() or depth == 0:
        result = state.get_result()
        if result == 'first':  return  100 + depth
        if result == 'second': return -(100 + depth)
        if result == 'draw':   return  0
        return heuristic(state)

    moves = state.get_moves()

    if is_max:
        best: float = float('-inf')
        for move in moves:
            val  = minimax(state.apply_move(move), depth - 1, False, counter)
            best = max(best, val)
        return best
    else:
        best: float = float('inf')
        for move in moves:
            val  = minimax(state.apply_move(move), depth - 1, True, counter)
            best = min(best, val)
        return best


def get_best_move(
    state: GameState,
    depth: int,
) -> dict[str, object]:
    """
    Find the best move for the current player using Minimax.

    Parameters
    ----------
    state : current game state
    depth : number of plies to search

    Returns
    -------
    dict with keys:
        move     : dict   — the best move found
        nodes    : int    — total nodes evaluated
        time_ms  : float  — time taken in milliseconds
    """
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
