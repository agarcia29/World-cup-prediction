import pandas as pd
from src.utils.constants import PROCESSED_DIR, MODELS_DIR
from src.utils.io import save_json


def main():
    df = pd.read_csv(PROCESSED_DIR / 'match_features.csv', parse_dates=['date'])
    teams = sorted(set(df['home_team']).union(df['away_team']))
    save_json(MODELS_DIR / 'teams.json', teams)
    print(f'{len(teams)} equipos exportados.')

if __name__ == '__main__':
    main()
