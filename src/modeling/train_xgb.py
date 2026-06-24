from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor
from src.utils.constants import MODELS_DIR
from src.utils.io import save_model, save_json

IGNORE_COLUMNS = {
    'date', 'home_team', 'away_team', 'home_score', 'away_score', 'country', 'goal_diff'
}

@dataclass
class TrainArtifacts:
    home_model: XGBRegressor
    away_model: XGBRegressor
    feature_columns: List[str]
    metrics: Dict[str, float]


def split_time(df: pd.DataFrame):
    train = df[df['date'] < '2025-01-01'].copy()
    valid = df[df['date'] >= '2025-01-01'].copy()
    return train, valid


def get_feature_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c not in IGNORE_COLUMNS and pd.api.types.is_numeric_dtype(df[c])]


def train_xgb_models(df: pd.DataFrame) -> TrainArtifacts:
    train_df, valid_df = split_time(df)
    features = get_feature_columns(df)
    X_train = train_df[features]
    X_valid = valid_df[features]

    home_model = XGBRegressor(
        n_estimators=80, max_depth=4, learning_rate=0.08,
        subsample=0.9, colsample_bytree=0.9, objective='reg:squarederror', random_state=42, n_jobs=2
    )
    away_model = XGBRegressor(
        n_estimators=80, max_depth=4, learning_rate=0.08,
        subsample=0.9, colsample_bytree=0.9, objective='reg:squarederror', random_state=42, n_jobs=2
    )
    home_model.fit(X_train, train_df['home_score'])
    away_model.fit(X_train, train_df['away_score'])

    home_pred = np.clip(home_model.predict(X_valid), 0, None)
    away_pred = np.clip(away_model.predict(X_valid), 0, None)
    metrics = {
        'home_mae': float(mean_absolute_error(valid_df['home_score'], home_pred)),
        'away_mae': float(mean_absolute_error(valid_df['away_score'], away_pred)),
        'home_rmse': float(np.sqrt(mean_squared_error(valid_df['home_score'], home_pred))),
        'away_rmse': float(np.sqrt(mean_squared_error(valid_df['away_score'], away_pred))),
    }
    return TrainArtifacts(home_model, away_model, features, metrics)


def persist_artifacts(artifacts: TrainArtifacts):
    save_model(artifacts.home_model, MODELS_DIR / 'xgb_home.pkl')
    save_model(artifacts.away_model, MODELS_DIR / 'xgb_away.pkl')
    save_json(MODELS_DIR / 'feature_columns.json', artifacts.feature_columns)
    save_json(MODELS_DIR / 'xgb_metrics.json', artifacts.metrics)
