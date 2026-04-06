import csv
import os


# Records completed games and exports results for the assignment report
class ExperimentTracker:

    def __init__(self) -> None:
        self.games: list[dict[str, object]] = []

    def record(
        self,
        algo:       str,
        depth:      int,
        length:     int,
        starter:    str,
        result:     str,
        nodes:      int,
        move_times: list[float],
        points:     int,
        bank:       int,
    ) -> None:
        # Append one completed game record; algo is 'minimax' or 'alphabeta',
        # result is 'first'/'second'/'draw', move_times are per-move durations in ms
        self.games.append({
            'game':    len(self.games) + 1,
            'algo':    algo,
            'depth':   depth,
            'length':  length,
            'starter': starter,
            'result':  result,
            'nodes':   nodes,
            'avg_ms':  self.average_time(move_times),
            'points':  points,
            'bank':    bank,
        })

    def average_time(self, move_times: list[float]) -> float:
        # Return average move time in ms rounded to 2 decimal places, or 0.0 if no moves
        if not move_times:
            return 0.0
        return round(sum(move_times) / len(move_times), 2)

    def summary(self) -> dict[str, dict[str, int]]:
        # Return win/loss/draw counts per algorithm ('minimax', 'alphabeta') plus a 'total' entry
        summary: dict[str, dict[str, int]] = {
            'minimax':   {'first': 0, 'second': 0, 'draw': 0},
            'alphabeta': {'first': 0, 'second': 0, 'draw': 0},
            'total':     {'first': 0, 'second': 0, 'draw': 0},
        }
        for game in self.games:
            algo:   str = game['algo']
            result: str = game['result']
            if algo in summary:
                summary[algo][result] += 1
            summary['total'][result] += 1
        return summary

    def export_csv(self, filepath: str) -> None:
        # Write all recorded games to a CSV file at the given filepath
        if not self.games:
            print('No experiments to export.')
            return

        fieldnames: list[str] = [
            'game', 'algo', 'depth', 'length', 'starter',
            'result', 'nodes', 'avg_ms', 'points', 'bank'
        ]

        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.games)

        print(f'Exported {len(self.games)} games to {os.path.abspath(filepath)}')

    def __len__(self) -> int:
        return len(self.games)

    def __repr__(self) -> str:
        return f'ExperimentTracker({len(self.games)} games recorded)'
