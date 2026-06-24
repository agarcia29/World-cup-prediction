from __future__ import annotations
import argparse
import pandas as pd
from src.utils.constants import PROCESSED_DIR
from src.modeling.train_bayes import fit_poisson_baseline, fit_pymc_hierarchical

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pymc', action='store_true', help='Train hierarchical PyMC model')
    parser.add_argument('--draws', type=int, default=1000)
    parser.add_argument('--tune', type=int, default=1000)
    args = parser.parse_args()

    df = pd.read_csv(PROCESSED_DIR / 'match_features.csv')
    fit_poisson_baseline(df)
    print('Saved fallback baseline bayes_baseline.json')

    if args.pymc:
        path = fit_pymc_hierarchical(df, draws=args.draws, tune=args.tune)
        print(f'Saved hierarchical PyMC posterior to {path}')

if __name__ == '__main__':
    main()
