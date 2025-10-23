# schemas/plays.py
from pydantic import BaseModel
from datetime import datetime
from typing import Any

class PlayBase(BaseModel):
    name: str

class PlayCreate(PlayBase):
    data: Any  # JSON que viene de Unity

class PlayCreateRequest(BaseModel):
    team_id: int
    name: str
    data: str

class PlayOut(PlayBase):
    id: int
    team_id: int
    created_at: datetime
    data: Any

    class Config:
        orm_mode = True
