from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from urllib.parse import urlencode

from . import models, schemas, database
from .auth import get_current_user

router = APIRouter()
  
# Database Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------------
# Add Media (Authenticated)
# -----------------------------------
@router.post("/media/", response_model=schemas.MediaAssetResponse)
def add_media(media: schemas.MediaAssetCreate, 
              db: Session = Depends(get_db), 
              current_user: models.AdminUser = Depends(get_current_user)):

    new_media = models.MediaAsset(
        title=media.title,
        type=media.type,
        file_url=media.file_url,
        created_at=datetime.utcnow()
    )
    db.add(new_media)
    db.commit()
    db.refresh(new_media)
    return new_media

# -----------------------------------
# Get Secure Stream URL (Authenticated)
# -----------------------------------
@router.get("/media/{id}/stream-url")
def get_stream_url(id: int, 
                   db: Session = Depends(get_db), 
                   current_user: models.AdminUser = Depends(get_current_user)):

    media_item = db.query(models.MediaAsset).filter(models.MediaAsset.id == id).first()
    if not media_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")

    # Create secure link valid for 10 minutes
    expires = datetime.utcnow() + timedelta(minutes=10)
    params = {
        "expires": expires.isoformat()
    }
    secure_url = f"{media_item.file_url}?{urlencode(params)}"

    return {"stream_url": secure_url}
