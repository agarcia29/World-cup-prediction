from __future__ import annotations
from pathlib import Path
from io import StringIO
import pandas as pd
from fastapi import UploadFile
from src.utils.constants import RAW_DIR, INTERIM_DIR, PROCESSED_DIR, MODELS_DIR
from src.utils.io import save_json
from src.data_pipeline.load_data import load_raw_csv
from src.data_pipeline.clean_results import clean_results
from src.data_pipeline.build_match_features import build_match_features
from src.modeling.train_xgb import train_xgb_models, persist_artifacts
from src.modeling.train_bayes import fit_poisson_baseline

REQUIRED_RESULTS_COLS = ['date','home_team','away_team','home_score','away_score','tournament','city','country','neutral']

class AdminService:
    def dataset_summary(self):
        summary = {}
        for name, path in {
            'raw_results': RAW_DIR / 'results.csv',
            'interim_results': INTERIM_DIR / 'results_2018.csv',
            'match_features': PROCESSED_DIR / 'match_features.csv',
            'teams': MODELS_DIR / 'teams.json',
        }.items():
            if path.exists():
                if path.suffix == '.json':
                    import json
                    data = json.loads(path.read_text(encoding='utf-8'))
                    summary[name] = {'exists': True, 'count': len(data)}
                else:
                    df = pd.read_csv(path)
                    item = {'exists': True, 'rows': int(len(df)), 'columns': list(df.columns)}
                    if 'date' in df.columns and len(df):
                        dates = pd.to_datetime(df['date'])
                        item['min_date'] = str(dates.min().date())
                        item['max_date'] = str(dates.max().date())
                    summary[name] = item
            else:
                summary[name] = {'exists': False}
        return summary

    async def upload_csv(self, file: UploadFile, target_name: str):
        raw = await file.read()
        text = raw.decode('utf-8-sig')
        df = pd.read_csv(StringIO(text))
        if target_name == 'results.csv':
            missing = [c for c in REQUIRED_RESULTS_COLS if c not in df.columns]
            if missing:
                raise ValueError(f'Faltan columnas en results.csv: {missing}')
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(RAW_DIR / target_name, index=False)
        return {'filename': target_name, 'rows': int(len(df))}

    def add_match(self, payload: dict):
        path = RAW_DIR / 'results.csv'
        df = pd.read_csv(path)
        new_row = pd.DataFrame([payload])
        combined = pd.concat([df, new_row], ignore_index=True)
        combined['date'] = pd.to_datetime(combined['date'])
        combined = combined.sort_values(['date','home_team','away_team']).drop_duplicates(subset=['date','home_team','away_team'], keep='last')
        combined['date'] = combined['date'].dt.strftime('%Y-%m-%d')
        combined.to_csv(path, index=False)
        return {'rows': int(len(combined))}

    def rebuild_features(self):
        results = load_raw_csv('results.csv')
        clean = clean_results(results)
        clean.to_csv(INTERIM_DIR / 'results_2018.csv', index=False)
        for name in ['goalscorers.csv','shootouts.csv']:
            src = RAW_DIR / name
            if src.exists():
                df = pd.read_csv(src, parse_dates=['date'])
                df = df[df['date'] >= pd.Timestamp('2018-01-01')]
                df.to_csv(INTERIM_DIR / name.replace('.csv','_2018.csv'), index=False)
        match_df, team_snapshots = build_match_features(clean)
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        match_df.to_csv(PROCESSED_DIR / 'match_features.csv', index=False)
        team_snapshots.to_csv(PROCESSED_DIR / 'team_snapshots.csv', index=False)
        return {'match_rows': int(len(match_df)), 'snapshot_rows': int(len(team_snapshots))}

    def retrain_xgb(self):
        df = pd.read_csv(PROCESSED_DIR / 'match_features.csv', parse_dates=['date'])
        artifacts = train_xgb_models(df)
        persist_artifacts(artifacts)
        return {'metrics': artifacts.metrics}

    def retrain_bayes_baseline(self):
        df = pd.read_csv(INTERIM_DIR / 'results_2018.csv', parse_dates=['date'])
        model = fit_poisson_baseline(df)
        return {'teams': len(model['attack'])}

    def refresh_teams(self):
        df = pd.read_csv(PROCESSED_DIR / 'match_features.csv')
        teams = sorted(set(df['home_team']).union(df['away_team']))
        save_json(MODELS_DIR / 'teams.json', teams)
        return {'teams': len(teams)}
