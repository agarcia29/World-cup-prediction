from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from src.utils.constants import MODELS_DIR

class BayesService:
    def __init__(self):
        self.baseline = json.loads((MODELS_DIR / 'bayes_baseline.json').read_text())
        self.team_index = None
        self.posterior = None
        team_index_path = MODELS_DIR / 'team_index.json'
        posterior_path = MODELS_DIR / 'bayes_pymc.nc'
        if team_index_path.exists() and posterior_path.exists():
            try:
                import arviz as az
                self.team_index = json.loads(team_index_path.read_text())
                self.posterior = az.from_netcdf(posterior_path)
            except Exception:
                self.team_index = None
                self.posterior = None

    def _baseline_predict(self, home_team: str, away_team: str, neutral: bool):
        attack = self.baseline['attack']
        defense = self.baseline['defense']
        g_home = self.baseline['global_home_avg']
        g_away = self.baseline['global_away_avg']
        home_att = attack.get(home_team, 1.0)
        away_att = attack.get(away_team, 1.0)
        home_def = defense.get(home_team, 1.0)
        away_def = defense.get(away_team, 1.0)
        home_adv = 1.08 if not neutral else 1.0
        return {
            'home': max(0.05, g_home * home_att * away_def * home_adv),
            'away': max(0.05, g_away * away_att * home_def / home_adv),
            'source': 'baseline',
        }

    def _posterior_predict(self, home_team: str, away_team: str, neutral: bool):
        if self.posterior is None or self.team_index is None:
            return None
        if home_team not in self.team_index or away_team not in self.team_index:
            return None

        post = self.posterior.posterior
        h = self.team_index[home_team]
        a = self.team_index[away_team]

        intercept = float(post['intercept'].mean().values)
        home_adv = float(post['home_adv'].mean().values)
        attack = post['attack'].mean(dim=('chain', 'draw')).values
        defense = post['defense'].mean(dim=('chain', 'draw')).values

        log_home = intercept + (0 if neutral else home_adv) + attack[h] - defense[a]
        log_away = intercept + attack[a] - defense[h]
        return {
            'home': float(np.exp(log_home)),
            'away': float(np.exp(log_away)),
            'source': 'pymc',
        }

    def predict_xg(self, home_team: str, away_team: str, neutral: bool):
        pred = self._posterior_predict(home_team, away_team, neutral)
        return pred or self._baseline_predict(home_team, away_team, neutral)
