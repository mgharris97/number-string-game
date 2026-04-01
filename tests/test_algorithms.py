"""
Tests for minimax.py and alphabeta.py
Run with: python -m pytest tests/test_algorithms.py -v
"""
import sys
import os
import random
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.game_state import GameState
from src.minimax import get_best_move as minimax_best, heuristic
from src.alphabeta import get_best_move as alphabeta_best


def make_state(length: int = 6, seed: int | None = None) -> GameState:
    """Helper — create a GameState with a short string for fast tests."""
    if seed is not None:
        random.seed(seed)
    nums: list[int] = [random.randint(1, 6) for _ in range(length)]
    return GameState(nums)


# ── Heuristic ─────────────────────────────────────────────────────────────────

def test_heuristic_returns_float() -> None:
    state: GameState = make_state(6, seed=1)
    result: float = heuristic(state)
    assert isinstance(result, float)

def test_heuristic_not_called_on_terminal() -> None:
    """Heuristic should never be needed on a terminal state."""
    state: GameState = GameState([3], points=1, bank=0)
    assert state.is_terminal() is True
    assert state.get_result() is not None   # result exists — no need for heuristic


# ── Minimax ───────────────────────────────────────────────────────────────────

def test_minimax_returns_valid_move() -> None:
    state: GameState = make_state(6, seed=42)
    result: dict = minimax_best(state, depth=3)
    assert result['move'] in state.get_moves()

def test_minimax_node_count_positive() -> None:
    state: GameState = make_state(6, seed=42)
    result: dict = minimax_best(state, depth=3)
    assert result['nodes'] > 0

def test_minimax_time_recorded() -> None:
    state: GameState = make_state(6, seed=42)
    result: dict = minimax_best(state, depth=3)
    assert result['time_ms'] >= 0.0

def test_minimax_deeper_generates_more_nodes() -> None:
    state: GameState    = make_state(6, seed=42)
    shallow: dict       = minimax_best(state, depth=2)
    deep: dict          = minimax_best(state, depth=4)
    assert deep['nodes'] >= shallow['nodes']

def test_minimax_returns_dict_keys() -> None:
    state: GameState = make_state(6, seed=42)
    result: dict = minimax_best(state, depth=3)
    assert 'move'    in result
    assert 'nodes'   in result
    assert 'time_ms' in result


# ── Alpha-Beta ────────────────────────────────────────────────────────────────

def test_alphabeta_returns_valid_move() -> None:
    state: GameState = make_state(6, seed=42)
    result: dict = alphabeta_best(state, depth=3)
    assert result['move'] in state.get_moves()

def test_alphabeta_node_count_positive() -> None:
    state: GameState = make_state(6, seed=42)
    result: dict = alphabeta_best(state, depth=3)
    assert result['nodes'] > 0

def test_alphabeta_time_recorded() -> None:
    state: GameState = make_state(6, seed=42)
    result: dict = alphabeta_best(state, depth=3)
    assert result['time_ms'] >= 0.0

def test_alphabeta_returns_dict_keys() -> None:
    state: GameState = make_state(6, seed=42)
    result: dict = alphabeta_best(state, depth=3)
    assert 'move'    in result
    assert 'nodes'   in result
    assert 'time_ms' in result


# ── Agreement — Alpha-Beta must match Minimax ─────────────────────────────────

@pytest.mark.parametrize("seed", [1, 2, 3, 4, 5, 10, 42, 99, 123, 256])
def test_alphabeta_agrees_with_minimax(seed: int) -> None:
    """
    Alpha-Beta must always choose the same move as Minimax at equal depth.
    Tested across 10 different random starting states.
    """
    state: GameState = make_state(6, seed=seed)
    mm: dict         = minimax_best(state,  depth=4)
    ab: dict         = alphabeta_best(state, depth=4)
    assert mm['move'] == ab['move'], (
        f"Seed {seed}: Minimax chose {mm['move']} but Alpha-Beta chose {ab['move']}"
    )


# ── Efficiency — Alpha-Beta must use fewer or equal nodes ─────────────────────

@pytest.mark.parametrize("seed", [1, 2, 3, 4, 5])
def test_alphabeta_fewer_or_equal_nodes(seed: int) -> None:
    """Alpha-Beta should never evaluate more nodes than Minimax."""
    state: GameState = make_state(6, seed=seed)
    mm: dict         = minimax_best(state,  depth=4)
    ab: dict         = alphabeta_best(state, depth=4)
    assert ab['nodes'] <= mm['nodes'], (
        f"Seed {seed}: Alpha-Beta used {ab['nodes']} nodes "
        f"but Minimax used {mm['nodes']}"
    )


# ── Experiments tracker ───────────────────────────────────────────────────────

def test_experiment_tracker_records_game() -> None:
    from src.experiments import ExperimentTracker
    tracker: ExperimentTracker = ExperimentTracker()
    tracker.record(
        algo='alphabeta', depth=4, length=16, starter='human',
        result='first', nodes=1243, move_times=[120.3, 98.7, 134.2],
        points=7, bank=2
    )
    assert len(tracker) == 1

def test_experiment_tracker_average_time() -> None:
    from src.experiments import ExperimentTracker
    tracker: ExperimentTracker = ExperimentTracker()
    avg: float = tracker.average_time([100.0, 200.0, 300.0])
    assert avg == 200.0

def test_experiment_tracker_average_time_empty() -> None:
    from src.experiments import ExperimentTracker
    tracker: ExperimentTracker = ExperimentTracker()
    assert tracker.average_time([]) == 0.0

def test_experiment_tracker_summary() -> None:
    from src.experiments import ExperimentTracker
    tracker: ExperimentTracker = ExperimentTracker()
    tracker.record('alphabeta', 4, 16, 'human',    'first',  1000, [100.0], 7, 2)
    tracker.record('minimax',   4, 16, 'computer', 'second', 2000, [200.0], 3, 1)
    tracker.record('alphabeta', 4, 16, 'human',    'draw',    800, [90.0],  5, 0)
    summary = tracker.summary()
    assert summary['alphabeta']['first']  == 1
    assert summary['alphabeta']['draw']   == 1
    assert summary['minimax']['second']   == 1
    assert summary['total']['first']      == 1
    assert summary['total']['second']     == 1
    assert summary['total']['draw']       == 1

def test_experiment_tracker_export_csv(tmp_path) -> None:
    from src.experiments import ExperimentTracker
    tracker: ExperimentTracker = ExperimentTracker()
    tracker.record('minimax', 4, 16, 'human', 'first', 1000, [100.0], 5, 1)
    fp = str(tmp_path / 'results.csv')
    tracker.export_csv(fp)
    assert os.path.exists(fp)
    with open(fp) as f:
        lines = f.readlines()
    assert len(lines) == 2   # header + 1 game
