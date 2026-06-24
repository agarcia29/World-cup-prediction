from __future__ import annotations

def combine_xg(bayes_home: float, bayes_away: float, xgb_home: float, xgb_away: float, bayes_weight: float = 0.60):
    xgb_weight = 1.0 - bayes_weight
    return {
        'home_xg': bayes_weight * bayes_home + xgb_weight * xgb_home,
        'away_xg': bayes_weight * bayes_away + xgb_weight * xgb_away,
    }
