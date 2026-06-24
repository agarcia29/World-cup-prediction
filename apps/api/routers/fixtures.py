from fastapi import APIRouter
from src.utils.constants import MODELS_DIR
from src.utils.io import load_json

router = APIRouter(prefix='/fixtures', tags=['fixtures'])

@router.get('/today')
def get_today_fixtures():
    path = MODELS_DIR / 'fixtures_today.json'
    if not path.exists():
        return {'fixtures': []}
    payload = load_json(path)
    if isinstance(payload, dict):
        return payload
    return {'fixtures': payload}
