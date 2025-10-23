from pydantic import BaseModel
from typing import Optional

# ---------------- Permission ----------------
class PermissionBase(BaseModel):
    role: str  # admin, editor, viewer

class PermissionCreate(PermissionBase):
    user_id: int

class PermissionOut(PermissionBase):
    team_id: int
    username: str
    team_name: str
    team_color: str
    owner: str  # username del admin/owner

    class Config:
        from_attributes = True
