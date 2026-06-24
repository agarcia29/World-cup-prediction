from fastapi import APIRouter
import json
from src.utils.constants import MODELS_DIR

router = APIRouter(prefix='/model-info', tags=['model-info'])

@router.get('')
def model_info():
    metrics = {}
    metrics_path = MODELS_DIR / 'xgb_metrics.json'
    if metrics_path.exists():
        metrics = json.loads(metrics_path.read_text())
    return {
        'data_window': '2018-01-01 to present',
        'models': {
            'bayes': 'Hierarchical PyMC if bayes_pymc.nc exists, else Poisson baseline',
            'xgboost': 'Two regressors for home and away goals'
        },
        'xgb_metrics': metrics,
    }
