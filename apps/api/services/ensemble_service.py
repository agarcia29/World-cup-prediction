from src.modeling.ensemble import combine_xg

class EnsembleService:
    def combine(self, bayes_pred: dict, xgb_pred: dict):
        return combine_xg(bayes_pred['home'], bayes_pred['away'], xgb_pred['home'], xgb_pred['away'])
