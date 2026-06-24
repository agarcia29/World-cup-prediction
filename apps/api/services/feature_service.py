from __future__ import annotations
import pandas as pd
from src.utils.constants import PROCESSED_DIR
from src.data_pipeline.tournament_weights import get_tournament_weight

ROLLING_WINDOWS = (3, 5, 10)
ROLL_METRICS = ['goals_for_avg','goals_against_avg','points_avg','win_avg','draw_avg','loss_avg','clean_sheet_avg','failed_to_score_avg']

class FeatureService:
    def __init__(self):
        self.df = pd.read_csv(PROCESSED_DIR / 'match_features.csv', parse_dates=['date'])
        self.snapshots = pd.read_csv(PROCESSED_DIR / 'team_snapshots.csv', parse_dates=['date'])

    def _latest_team_snapshot(self, team: str) -> dict:
        team_rows = self.snapshots[self.snapshots['team'] == team].sort_values('date')
        if team_rows.empty:
            raise ValueError(f'No hay historial para {team}')
        return team_rows.iloc[-1].to_dict()

    def _latest_elo(self, team: str) -> float:
        home = self.df[self.df['home_team'] == team][['date', 'elo_home_pre']].rename(columns={'elo_home_pre': 'elo'})
        away = self.df[self.df['away_team'] == team][['date', 'elo_away_pre']].rename(columns={'elo_away_pre': 'elo'})
        both = pd.concat([home, away]).sort_values('date')
        if both.empty:
            raise ValueError(f'No hay Elo para {team}')
        return float(both.iloc[-1]['elo'])

    def build_prediction_row(self, home_team: str, away_team: str, neutral: bool, tournament: str, month: int = 6) -> pd.DataFrame:
        home_row = self._latest_team_snapshot(home_team)
        away_row = self._latest_team_snapshot(away_team)
        payload = {
            'neutral': int(neutral),
            'tournament_weight': get_tournament_weight(tournament),
            'month': int(month),
            'elo_home_pre': self._latest_elo(home_team),
            'elo_away_pre': self._latest_elo(away_team),
        }
        payload['elo_diff_pre'] = payload['elo_home_pre'] - payload['elo_away_pre']
        for window in ROLLING_WINDOWS:
            for metric in ROLL_METRICS:
                payload[f'home_{metric}_{window}'] = home_row.get(f'{metric}_{window}', 0.0)
                payload[f'away_{metric}_{window}'] = away_row.get(f'{metric}_{window}', 0.0)
            payload[f'gf_form_diff_{window}'] = payload[f'home_goals_for_avg_{window}'] - payload[f'away_goals_for_avg_{window}']
            payload[f'ga_form_diff_{window}'] = payload[f'home_goals_against_avg_{window}'] - payload[f'away_goals_against_avg_{window}']
            payload[f'points_form_diff_{window}'] = payload[f'home_points_avg_{window}'] - payload[f'away_points_avg_{window}']
        return pd.DataFrame([payload])
