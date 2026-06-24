from src.utils.constants import TOURNAMENT_WEIGHTS, DEFAULT_TOURNAMENT_WEIGHT

def get_tournament_weight(name: str) -> float:
    return TOURNAMENT_WEIGHTS.get(name, DEFAULT_TOURNAMENT_WEIGHT)
