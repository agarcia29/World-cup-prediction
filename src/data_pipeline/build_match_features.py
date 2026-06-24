from __future__ import annotations
import numpy as np
import pandas as pd
from src.data_pipeline.build_team_elo import build_elo_features

ROLLING_WINDOWS = (3, 5, 10)
BASE_COLS = ['goals_for', 'goals_against', 'points', 'win', 'draw', 'loss', 'clean_sheet', 'failed_to_score']


def _long_team_matches(results: pd.DataFrame) -> pd.DataFrame:
    home = results[['date', 'home_team', 'away_team', 'home_score', 'away_score', 'tournament_weight', 'neutral', 'tournament']].copy()
    home = home.rename(columns={'home_team': 'team', 'away_team': 'opponent'})
    home['is_home'] = 1
    home['goals_for'] = home['home_score']
    home['goals_against'] = home['away_score']

    away = results[['date', 'home_team', 'away_team', 'home_score', 'away_score', 'tournament_weight', 'neutral', 'tournament']].copy()
    away = away.rename(columns={'away_team': 'team', 'home_team': 'opponent'})
    away['is_home'] = 0
    away['goals_for'] = away['away_score']
    away['goals_against'] = away['home_score']

    long_df = pd.concat([home, away], ignore_index=True)
    long_df['points'] = np.select(
        [long_df['goals_for'] > long_df['goals_against'], long_df['goals_for'] == long_df['goals_against']],
        [3, 1],
        default=0,
    )
    long_df['win'] = (long_df['goals_for'] > long_df['goals_against']).astype(int)
    long_df['draw'] = (long_df['goals_for'] == long_df['goals_against']).astype(int)
    long_df['loss'] = (long_df['goals_for'] < long_df['goals_against']).astype(int)
    long_df['clean_sheet'] = (long_df['goals_against'] == 0).astype(int)
    long_df['failed_to_score'] = (long_df['goals_for'] == 0).astype(int)
    return long_df.sort_values(['team', 'date']).reset_index(drop=True)


def _add_team_rolling_features(long_df: pd.DataFrame) -> pd.DataFrame:
    long_df = long_df.copy()
    grouped = long_df.groupby('team', group_keys=False)
    shifted = grouped[BASE_COLS].shift(1)

    for window in ROLLING_WINDOWS:
        rolled = (
            shifted.groupby(long_df['team'])
            .rolling(window=window, min_periods=1)
            .mean()
            .reset_index(level=0, drop=True)
        )
        for col in BASE_COLS:
            long_df[f'{col}_avg_{window}'] = rolled[col]

    long_df['matches_played_before'] = grouped.cumcount()
    long_df['days_since_prev_match'] = grouped['date'].diff().dt.days.fillna(999).clip(upper=999)
    return long_df


def _team_feature_snapshot(long_df: pd.DataFrame) -> pd.DataFrame:
    """One row per team-match with ONLY pre-match features."""
    keep = ['date', 'team', 'is_home', 'matches_played_before', 'days_since_prev_match']
    for w in ROLLING_WINDOWS:
        keep += [f'{c}_avg_{w}' for c in BASE_COLS]
    return long_df[keep].copy()


def _merge_side_features(results: pd.DataFrame, team_features: pd.DataFrame, side: str) -> pd.DataFrame:
    team_col = 'home_team' if side == 'home' else 'away_team'
    side_features = team_features.rename(columns={'team': team_col})
    side_features = side_features.add_prefix(f'{side}_')
    side_features = side_features.rename(columns={f'{side}_date': 'date', f'{side}_{team_col}': team_col})
    merged = results.merge(side_features, on=['date', team_col], how='left')
    return merged


def build_match_features(results: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Returns:
      - match_features: one row per match for model training
      - team_snapshots: latest pre-match state per team-match, useful for inference
    """
    results = results.sort_values('date').reset_index(drop=True).copy()
    elo_df = build_elo_features(results)
    long_df = _long_team_matches(elo_df)
    long_df = _add_team_rolling_features(long_df)
    team_features = _team_feature_snapshot(long_df)

    df = elo_df.copy()
    df = _merge_side_features(df, team_features, 'home')
    df = _merge_side_features(df, team_features, 'away')
    df['month'] = pd.to_datetime(df['date']).dt.month.astype(int)

    for w in ROLLING_WINDOWS:
        df[f'gf_form_diff_{w}'] = df[f'home_goals_for_avg_{w}'] - df[f'away_goals_for_avg_{w}']
        df[f'ga_form_diff_{w}'] = df[f'home_goals_against_avg_{w}'] - df[f'away_goals_against_avg_{w}']
        df[f'points_form_diff_{w}'] = df[f'home_points_avg_{w}'] - df[f'away_points_avg_{w}']

    numeric_cols = [c for c in df.columns if c not in {'date', 'home_team', 'away_team', 'tournament', 'country'}]
    df[numeric_cols] = df[numeric_cols].replace([np.inf, -np.inf], np.nan)
    # Only fill feature NaNs; targets stay untouched
    feature_cols = [c for c in numeric_cols if c not in {'home_score', 'away_score'}]
    df[feature_cols] = df[feature_cols].fillna(0.0)

    return df, team_features
