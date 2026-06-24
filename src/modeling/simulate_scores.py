from __future__ import annotations
import math
from src.utils.constants import MAX_GOALS


def poisson_pmf(k: int, lam: float) -> float:
    return math.exp(-lam) * (lam ** k) / math.factorial(k)


def _poisson_distribution(lam: float, max_goals: int):
    probs = [poisson_pmf(i, lam) for i in range(max_goals + 1)]
    tail = max(0.0, 1 - sum(probs))
    probs[-1] += tail
    total = sum(probs)
    return [p / total for p in probs]


def score_matrix(home_xg: float, away_xg: float, max_goals: int = MAX_GOALS):
    home_dist = _poisson_distribution(home_xg, max_goals)
    away_dist = _poisson_distribution(away_xg, max_goals)
    matrix = []
    for i in range(max_goals + 1):
        row = []
        for j in range(max_goals + 1):
            row.append(home_dist[i] * away_dist[j])
        matrix.append(row)
    total = sum(sum(r) for r in matrix)
    matrix = [[v / total for v in r] for r in matrix]
    return matrix


def summarize_matrix(matrix):
    home_win = draw = away_win = 0.0
    over_25 = under_25 = btts_yes = btts_no = 0.0
    scorelines = []
    home_goal_dist = [0.0 for _ in range(len(matrix))]
    away_goal_dist = [0.0 for _ in range(len(matrix[0]))]
    for i, row in enumerate(matrix):
        for j, p in enumerate(row):
            home_goal_dist[i] += p
            away_goal_dist[j] += p
            if i > j:
                home_win += p
            elif i == j:
                draw += p
            else:
                away_win += p
            if i + j >= 3:
                over_25 += p
            else:
                under_25 += p
            if i > 0 and j > 0:
                btts_yes += p
            else:
                btts_no += p
            scorelines.append({'home_goals': i, 'away_goals': j, 'probability': p})
    scorelines.sort(key=lambda x: x['probability'], reverse=True)
    return {
        'probabilities_1x2': {'home_win': home_win, 'draw': draw, 'away_win': away_win},
        'market_probs': {
            'over_2_5': over_25,
            'under_2_5': under_25,
            'btts_yes': btts_yes,
            'btts_no': btts_no,
        },
        'goal_distributions': {
            'home': home_goal_dist,
            'away': away_goal_dist,
        },
        'top_scorelines': scorelines[:10],
    }
