from __future__ import annotations
import pandas as pd
from src.utils.constants import INTERIM_DIR, PROCESSED_DIR
from src.data_pipeline.build_match_features import build_match_features

def main():
    results = pd.read_csv(INTERIM_DIR / 'results_2018.csv', parse_dates=['date'])
    match_df, team_snapshots = build_match_features(results)
    match_df.to_csv(PROCESSED_DIR / 'match_features.csv', index=False)
    team_snapshots.to_csv(PROCESSED_DIR / 'team_snapshots.csv', index=False)
    print(f"Saved match features: {len(match_df):,} rows")
    print(f"Saved team snapshots: {len(team_snapshots):,} rows")

if __name__ == '__main__':
    main()
