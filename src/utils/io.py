import json
from pathlib import Path
import joblib
import pandas as pd


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_json(path: Path, payload):
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def save_df(df: pd.DataFrame, path: Path):
    ensure_dir(path.parent)
    if path.suffix == '.parquet':
        df.to_parquet(path, index=False)
    else:
        df.to_csv(path, index=False)


def load_df(path: Path) -> pd.DataFrame:
    if path.suffix == '.parquet':
        return pd.read_parquet(path)
    return pd.read_csv(path)


def save_model(model, path: Path):
    ensure_dir(path.parent)
    joblib.dump(model, path)


def load_model(path: Path):
    return joblib.load(path)
