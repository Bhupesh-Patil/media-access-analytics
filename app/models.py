from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from .database import Base

class AdminUser(Base):
    __tablename__ = "admin_users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class MediaAsset(Base):
    __tablename__ = "media_assets"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    type = Column(String, nullable=False)  # video or audio
    file_url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class MediaViewLog(Base):
    __tablename__ = "media_view_logs"
    id = Column(Integer, primary_key=True, index=True)
    media_id = Column(Integer, ForeignKey("media_assets.id"), nullable=False)
    viewed_by_ip = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
