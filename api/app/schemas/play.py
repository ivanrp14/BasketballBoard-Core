from typing import Any, Dict, Optional
from pydantic import BaseModel
from datetime import datetime

class PlayCreate(BaseModel):
    name: str
    data: Dict[str, Any]  # contenido de la jugada (irá a Mongo)


class PlayOut(BaseModel):
    id: int
    team_id: int
    name: str
    created_at: datetime
    data: Optional[Dict[str, Any]]  # se incluirá al traer desde Mongo

    class Config:
        orm_mode = True
