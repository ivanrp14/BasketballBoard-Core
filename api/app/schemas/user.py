# schemas.py
from pydantic import BaseModel, EmailStr
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str

   
    model_config = {
        "from_attributes": True  # This replaces the old Config class in Pydantic v2
    }

class Token(BaseModel):
    access_token: str
    token_type: str
