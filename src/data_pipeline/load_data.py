from pathlib import Path
import pandas as pd
from src.utils.constants import RAW_DIR


def load_raw_csv(name: str) -> pd.DataFrame:
    path = RAW_DIR / name
    if not path.exists():
        raise FileNotFoundError(f'No encontré {path}. Copia los CSV originales a data/raw/.')
    return pd.read_csv(path)
