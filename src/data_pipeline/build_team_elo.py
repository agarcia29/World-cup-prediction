import math
import pandas as pd

BASE_ELO = 1500.0
HOME_ADVANTAGE = 50.0


def expected_score(r_a: float, r_b: float) -> float:
    return 1 / (1 + 10 ** ((r_b - r_a) / 400))


def match_result(home_score: int, away_score: int) -> tuple[float, float]:
    if home_score > away_score:
        return 1.0, 0.0
    if home_score < away_score:
        return 0.0, 1.0
    return 0.5, 0.5


def build_elo_features(matches: pd.DataFrame, k_base: float = 20.0) -> pd.DataFrame:
    df = matches.copy().sort_values('date').reset_index(drop=True)
    ratings: dict[str, float] = {}
    rows = []
    for _, row in df.iterrows():
        home = row['home_team']
        away = row['away_team']
        neutral = bool(row['neutral'])
        home_elo = ratings.get(home, BASE_ELO)
        away_elo = ratings.get(away, BASE_ELO)
        adj_home = home_elo if neutral else home_elo + HOME_ADVANTAGE
        exp_home = expected_score(adj_home, away_elo)
        exp_away = 1 - exp_home
        rows.append({
            'elo_home_pre': home_elo,
            'elo_away_pre': away_elo,
            'elo_diff_pre': home_elo - away_elo,
            'elo_home_win_exp': exp_home,
        })
        home_result, away_result = match_result(int(row['home_score']), int(row['away_score']))
        goal_margin = abs(int(row['home_score']) - int(row['away_score']))
        margin_multiplier = math.log(goal_margin + 1.0) + 1.0
        k = k_base * float(row.get('tournament_weight', 1.0)) * margin_multiplier
        ratings[home] = home_elo + k * (home_result - exp_home)
        ratings[away] = away_elo + k * (away_result - exp_away)
    elo_df = pd.DataFrame(rows)
    return pd.concat([df.reset_index(drop=True), elo_df], axis=1)
