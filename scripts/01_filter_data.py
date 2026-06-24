from src.data_pipeline.load_data import load_raw_csv
from src.data_pipeline.clean_results import clean_results
from src.utils.constants import INTERIM_DIR, START_DATE
from src.utils.io import save_df
import pandas as pd


def main():
    results = load_raw_csv('results.csv')
    goalscorers = load_raw_csv('goalscorers.csv')
    shootouts = load_raw_csv('shootouts.csv')

    clean = clean_results(results)
    save_df(clean, INTERIM_DIR / 'results_2018.csv')

    for name, df in [('goalscorers_2018.csv', goalscorers), ('shootouts_2018.csv', shootouts)]:
        df['date'] = pd.to_datetime(df['date'])
        filtered = df[df['date'] >= pd.Timestamp(START_DATE)].copy()
        save_df(filtered, INTERIM_DIR / name)

    print(f'Results filtrados: {len(clean)}')

if __name__ == '__main__':
    main()
