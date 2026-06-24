from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / 'data'
RAW_DIR = DATA_DIR / 'raw'
INTERIM_DIR = DATA_DIR / 'interim'
PROCESSED_DIR = DATA_DIR / 'processed'
MODELS_DIR = DATA_DIR / 'models'
START_DATE = '2018-01-01'
MAX_GOALS = 6
TOURNAMENT_WEIGHTS = {
    'FIFA World Cup': 1.00,
    'UEFA Euro': 0.95,
    'Copa América': 0.95,
    'FIFA World Cup qualification': 0.90,
    'UEFA Euro qualification': 0.85,
    'UEFA Nations League': 0.75,
    'CONMEBOL Nations League': 0.75,
    'Friendly': 0.45,
}
DEFAULT_TOURNAMENT_WEIGHT = 0.70
