from pydantic import BaseModel

class PermissionBase(BaseModel):
    role: str  # admin, editor, viewer

class PermissionCreate(PermissionBase):
    user_id: int

class PermissionOut(PermissionBase):
    id: int
    user_id: int
    team_id: int
    class Config:
        orm_mode = True