from fastapi import APIRouter
from apps.api.schemas.predict import PredictRequest, PredictResponse, CompareRequest
from apps.api.services.prediction_service import PredictionService

router = APIRouter(tags=['predict'])
service = PredictionService()

@router.post('/predict', response_model=PredictResponse)
def predict(payload: PredictRequest):
    return service.predict(
        home_team=payload.home_team,
        away_team=payload.away_team,
        neutral=payload.neutral,
        tournament=payload.tournament,
        month=payload.month,
    )

@router.post('/compare')
def compare(payload: CompareRequest):
    results = []
    for match in payload.matches:
        results.append(service.predict(
            home_team=match.home_team,
            away_team=match.away_team,
            neutral=match.neutral,
            tournament=match.tournament,
            month=match.month,
        ))
    return {'matches': results}
