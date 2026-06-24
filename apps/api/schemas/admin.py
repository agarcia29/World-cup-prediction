from pydantic import BaseModel, Field

class AddMatchRequest(BaseModel):
    date: str
    home_team: str
    away_team: str
    home_score: int = Field(ge=0)
    away_score: int = Field(ge=0)
    tournament: str
    city: str
    country: str
    neutral: bool = True
