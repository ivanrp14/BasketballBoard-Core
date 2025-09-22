from pydantic import BaseModel

class PermissionBase(BaseModel):
    role: str  # admin, editor, viewer

class PermissionCreate(PermissionBase):
    user_id: int

class PermissionOut(PermissionBase):
    username: str
    team_name: str
    team_color: str
    role: str
    class Config:
        orm_mode = True