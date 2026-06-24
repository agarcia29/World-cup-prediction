from __future__ import annotations
from apps.api.services.feature_service import FeatureService
from apps.api.services.bayes_service import BayesService
from apps.api.services.xgb_service import XGBService
from apps.api.services.ensemble_service import EnsembleService
from src.modeling.simulate_scores import score_matrix, summarize_matrix

class PredictionService:
    def __init__(self):
        self.feature_service = FeatureService()
        self.bayes = BayesService()
        self.xgb = XGBService()
        self.ensemble = EnsembleService()

    def predict(self, home_team: str, away_team: str, neutral: bool, tournament: str, month: int = 6):
        feature_row = self.feature_service.build_prediction_row(home_team, away_team, neutral, tournament, month=month)
        bayes_pred = self.bayes.predict_xg(home_team, away_team, neutral)
        xgb_pred = self.xgb.predict_xg(feature_row)
        final_xg = self.ensemble.combine(bayes_pred, xgb_pred)
        matrix = score_matrix(final_xg['home_xg'], final_xg['away_xg'])
        summary = summarize_matrix(matrix)
        insights = {
            'elo_diff': round(float(feature_row.iloc[0]['elo_diff_pre']), 1),
            'home_recent_gf_5': round(float(feature_row.iloc[0]['home_goals_for_avg_5']), 2),
            'away_recent_gf_5': round(float(feature_row.iloc[0]['away_goals_for_avg_5']), 2),
            'home_recent_ga_5': round(float(feature_row.iloc[0]['home_goals_against_avg_5']), 2),
            'away_recent_ga_5': round(float(feature_row.iloc[0]['away_goals_against_avg_5']), 2),
            'points_form_diff_5': round(float(feature_row.iloc[0]['points_form_diff_5']), 2),
            'bayes_source': bayes_pred.get('source', 'baseline'),
        }
        return {
            'input': {
                'home_team': home_team,
                'away_team': away_team,
                'neutral': neutral,
                'tournament': tournament,
                'month': month,
            },
            'expected_goals': {
                'home': round(final_xg['home_xg'], 3),
                'away': round(final_xg['away_xg'], 3),
            },
            'probabilities_1x2': {k: round(v, 4) for k, v in summary['probabilities_1x2'].items()},
            'market_probs': {k: round(v, 4) for k, v in summary['market_probs'].items()},
            'goal_distributions': {
                'home': [round(v, 6) for v in summary['goal_distributions']['home']],
                'away': [round(v, 6) for v in summary['goal_distributions']['away']],
            },
            'top_scorelines': [{**s, 'probability': round(s['probability'], 4)} for s in summary['top_scorelines']],
            'score_matrix': matrix,
            'model_breakdown': {
                'bayes_home_xg': round(bayes_pred['home'], 3),
                'bayes_away_xg': round(bayes_pred['away'], 3),
                'xgb_home_xg': round(xgb_pred['home'], 3),
                'xgb_away_xg': round(xgb_pred['away'], 3),
            },
            'insights': insights,
        }
