from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from src.utils.constants import MODELS_DIR
from src.utils.io import save_json

def fit_poisson_baseline(df: pd.DataFrame):
    """
    Fast fallback model used by the API if a PyMC posterior is not available.
    """
    home_avg = float(df['home_score'].mean())
    away_avg = float(df['away_score'].mean())
    league_avg = max((home_avg + away_avg) / 2, 1e-6)
    attack, defense = {}, {}
    teams = sorted(set(df['home_team']).union(df['away_team']))
    for team in teams:
        home = df[df['home_team'] == team]
        away = df[df['away_team'] == team]
        gf = pd.concat([home['home_score'], away['away_score']]).mean()
        ga = pd.concat([home['away_score'], away['home_score']]).mean()
        attack[team] = float((gf if pd.notna(gf) else league_avg) / league_avg)
        defense[team] = float((ga if pd.notna(ga) else league_avg) / league_avg)
    artifact = {
        'global_home_avg': home_avg,
        'global_away_avg': away_avg,
        'league_avg': league_avg,
        'attack': attack,
        'defense': defense,
    }
    save_json(MODELS_DIR / 'bayes_baseline.json', artifact)
    return artifact


def fit_pymc_hierarchical(
    df: pd.DataFrame,
    draws: int = 1000,
    tune: int = 1000,
    target_accept: float = 0.92,
    random_seed: int = 42,
    out_path: str | Path | None = None,
):
    """
    Hierarchical Poisson model:
      log(mu_home) = intercept + home_adv*(1-neutral) + attack_home - defense_away
      log(mu_away) = intercept + attack_away - defense_home

    Requires PyMC + ArviZ. We keep it isolated here so the rest of the app can
    still run with the fallback baseline.
    """
    import pymc as pm
    import arviz as az

    model_df = df[['home_team', 'away_team', 'home_score', 'away_score', 'neutral']].copy()
    teams = sorted(set(model_df['home_team']).union(model_df['away_team']))
    team_to_idx = {t: i for i, t in enumerate(teams)}
    home_idx = model_df['home_team'].map(team_to_idx).values
    away_idx = model_df['away_team'].map(team_to_idx).values

    with pm.Model() as model:
        intercept = pm.Normal('intercept', mu=np.log(max(model_df[['home_score','away_score']].stack().mean(), 1e-3)), sigma=1.0)
        home_adv = pm.Normal('home_adv', mu=0.15, sigma=0.25)

        attack_raw = pm.Normal('attack_raw', mu=0.0, sigma=0.35, shape=len(teams))
        defense_raw = pm.Normal('defense_raw', mu=0.0, sigma=0.35, shape=len(teams))
        attack = pm.Deterministic('attack', attack_raw - pm.math.mean(attack_raw))
        defense = pm.Deterministic('defense', defense_raw - pm.math.mean(defense_raw))

        log_mu_home = intercept + home_adv * (1 - model_df['neutral'].astype(int).values) + attack[home_idx] - defense[away_idx]
        log_mu_away = intercept + attack[away_idx] - defense[home_idx]

        pm.Poisson('home_goals', mu=pm.math.exp(log_mu_home), observed=model_df['home_score'].values)
        pm.Poisson('away_goals', mu=pm.math.exp(log_mu_away), observed=model_df['away_score'].values)

        idata = pm.sample(
            draws=draws,
            tune=tune,
            target_accept=target_accept,
            random_seed=random_seed,
            chains=2,
            cores=1,
            progressbar=True,
        )

    out_path = Path(out_path or MODELS_DIR / 'bayes_pymc.nc')
    az.to_netcdf(idata, out_path)
    save_json(MODELS_DIR / 'team_index.json', team_to_idx)
    return out_path
