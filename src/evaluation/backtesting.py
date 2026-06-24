from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor
from src.utils.constants import MODELS_DIR

TARGETS = ['home_score', 'away_score']
DROP_COLS = ['date', 'home_team', 'away_team', 'tournament', 'country', 'home_score', 'away_score']

def temporal_train_test_split(df: pd.DataFrame, test_start: str = '2025-01-01'):
    df = df.sort_values('date').copy()
    train = df[df['date'] < test_start].copy()
    test = df[df['date'] >= test_start].copy()
    return train, test

def build_xy(df: pd.DataFrame):
    X = df.drop(columns=[c for c in DROP_COLS if c in df.columns], errors='ignore')
    y_home = df['home_score'].astype(float)
    y_away = df['away_score'].astype(float)
    return X, y_home, y_away

def run_backtest(df: pd.DataFrame):
    train, test = temporal_train_test_split(df)
    X_train, y_home_train, y_away_train = build_xy(train)
    X_test, y_home_test, y_away_test = build_xy(test)

    params = dict(
        n_estimators=250, max_depth=4, learning_rate=0.05,
        subsample=0.9, colsample_bytree=0.9, random_state=42
    )
    home_model = XGBRegressor(**params)
    away_model = XGBRegressor(**params)
    home_model.fit(X_train, y_home_train)
    away_model.fit(X_train, y_away_train)

    pred_home = home_model.predict(X_test)
    pred_away = away_model.predict(X_test)

    metrics = {
        'test_matches': int(len(test)),
        'home_mae': float(mean_absolute_error(y_home_test, pred_home)),
        'away_mae': float(mean_absolute_error(y_away_test, pred_away)),
        'home_rmse': float(np.sqrt(mean_squared_error(y_home_test, pred_home))),
        'away_rmse': float(np.sqrt(mean_squared_error(y_away_test, pred_away))),
        'test_start': '2025-01-01',
    }
    (MODELS_DIR / 'backtest_metrics.json').write_text(json.dumps(metrics, indent=2))
    return metrics
