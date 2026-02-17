from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    name: str
    email: str
    password: str

class UserCreate(UserBase):
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    
    class Config:
        from_attributes = True
