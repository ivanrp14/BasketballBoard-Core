from typing import Optional
from pydantic import BaseModel

class TeamBase(BaseModel):
    name: str
    color: str

class TeamCreate(TeamBase):
    pass

class TeamOut(TeamBase):
    id: int
    invitation_code: str

    class Config:
        from_attributes = True  # <- importante para from_orm()