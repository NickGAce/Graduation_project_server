from pydantic import BaseModel, Field
from typing import Optional


class RatingCreate(BaseModel):
    resident_id: int = Field(description="The ID of the resident this rating belongs to.")
    achievement_score: float = Field(default=0.0, description="Score based on resident's achievements.")
    infraction_score: float = Field(default=0.0, description="Score based on resident's infractions.")


class RatingUpdate(BaseModel):
    achievement_score: Optional[float] = Field(None, description="Score based on resident's achievements.")
    infraction_score: Optional[float] = Field(None, description="Score based on resident's infractions.")
