import pandas as pd
from src.modeling.train_xgb import train_xgb_models, persist_artifacts
from src.utils.constants import PROCESSED_DIR


def main():
    df = pd.read_csv(PROCESSED_DIR / 'match_features.csv', parse_dates=['date'])
    artifacts = train_xgb_models(df)
    persist_artifacts(artifacts)
    print(artifacts.metrics)

if __name__ == '__main__':
    main()
