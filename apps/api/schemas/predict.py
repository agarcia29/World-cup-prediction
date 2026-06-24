from pydantic import BaseModel, Field
from typing import List, Dict

class PredictRequest(BaseModel):
    home_team: str
    away_team: str
    neutral: bool = True
    tournament: str = 'FIFA World Cup'
    month: int = Field(default=6, ge=1, le=12)

class Scoreline(BaseModel):
    home_goals: int
    away_goals: int
    probability: float

class PredictResponse(BaseModel):
    input: Dict
    expected_goals: Dict[str, float]
    probabilities_1x2: Dict[str, float]
    market_probs: Dict[str, float]
    goal_distributions: Dict[str, List[float]]
    top_scorelines: List[Scoreline]
    score_matrix: List[List[float]]
    model_breakdown: Dict[str, float]
    insights: Dict

class CompareRequest(BaseModel):
    matches: List[PredictRequest]
