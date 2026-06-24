from fastapi import APIRouter
from src.utils.constants import MODELS_DIR
from src.utils.io import load_json

router = APIRouter(prefix='/teams', tags=['teams'])

@router.get('')
def get_teams():
    return {'teams': load_json(MODELS_DIR / 'teams.json')}
