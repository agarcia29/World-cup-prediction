import pandas as pd
from src.utils.constants import START_DATE
from src.data_pipeline.tournament_weights import get_tournament_weight

REQUIRED_COLUMNS = [
    'date', 'home_team', 'away_team', 'home_score', 'away_score', 'tournament', 'country', 'neutral'
]


def clean_results(results: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in REQUIRED_COLUMNS if c not in results.columns]
    if missing:
        raise ValueError(f'Faltan columnas requeridas en results.csv: {missing}')

    df = results.copy()
    df = df[REQUIRED_COLUMNS].dropna(subset=['date', 'home_team', 'away_team', 'home_score', 'away_score'])
    df['date'] = pd.to_datetime(df['date'])
    df = df[df['date'] >= pd.Timestamp(START_DATE)].copy()
    df['home_score'] = df['home_score'].astype(int)
    df['away_score'] = df['away_score'].astype(int)
    df['neutral'] = df['neutral'].astype(bool)
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['tournament_weight'] = df['tournament'].map(get_tournament_weight)
    df['goal_diff'] = df['home_score'] - df['away_score']
    return df.sort_values('date').reset_index(drop=True)
