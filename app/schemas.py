# app/schemas.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Dict

# Admin User Schemas
class AdminUserCreate(BaseModel):
    email: EmailStr
    password: str

class AdminUserLogin(BaseModel):
    email: EmailStr
    password: str

# Media Asset Schemas
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

# Media Analytics Schemas
class MediaAnalyticsResponse(BaseModel):
    total_views: int
    unique_ips: int
    views_per_day: Dict[str, int]
