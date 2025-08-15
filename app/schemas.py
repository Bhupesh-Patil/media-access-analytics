from pydantic import BaseModel, EmailStr
from datetime import datetime

class AdminUserCreate(BaseModel):
    email: EmailStr
    password: str

class AdminUserLogin(BaseModel):
    email: EmailStr
    password: str

class MediaAssetCreate(BaseModel):
    title: str
    type: str
    file_url: str

class MediaAssetResponse(BaseModel):
    id: int
    title: str
    type: str
    file_url: str
    created_at: datetime

    class Config:
        orm_mode = True
