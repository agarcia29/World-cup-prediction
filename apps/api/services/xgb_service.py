from __future__ import annotations
import numpy as np
from src.utils.constants import MODELS_DIR
from src.utils.io import load_json, load_model

class XGBService:
    def __init__(self):
        self.home_model = load_model(MODELS_DIR / 'xgb_home.pkl')
        self.away_model = load_model(MODELS_DIR / 'xgb_away.pkl')
        self.feature_columns = load_json(MODELS_DIR / 'feature_columns.json')

    def predict_xg(self, feature_row):
        X = feature_row.reindex(columns=self.feature_columns, fill_value=0.0)
        home = float(np.clip(self.home_model.predict(X)[0], 0, None))
        away = float(np.clip(self.away_model.predict(X)[0], 0, None))
        return {'home': home, 'away': away}
