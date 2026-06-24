from __future__ import annotations
import pandas as pd
from src.utils.constants import PROCESSED_DIR
from src.evaluation.backtesting import run_backtest

def main():
    df = pd.read_csv(PROCESSED_DIR / 'match_features.csv', parse_dates=['date'])
    metrics = run_backtest(df)
    print(metrics)

if __name__ == '__main__':
    main()
