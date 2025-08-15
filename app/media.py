from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from datetime import datetime
from collections import defaultdict

from . import models, schemas, database
from .auth import get_current_user

router = APIRouter()

# -------------------------
# Database Dependency
# -------------------------
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------
# Add Media (Authenticated)
# -------------------------
@router.post("/", response_model=schemas.MediaAssetResponse)
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

# -------------------------
# Get Secure Stream URL (Authenticated)
# -------------------------
@router.get("/{id}/stream-url")
def get_stream_url(id: int, 
                   db: Session = Depends(get_db), 
                   current_user: models.AdminUser = Depends(get_current_user)):

    media_item = db.query(models.MediaAsset).filter(models.MediaAsset.id == id).first()
    if not media_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")

    return {"stream_url": media_item.file_url}

# -------------------------
# Log a Media View (Authenticated)
# -------------------------
@router.post("/{id}/view")
def log_media_view(id: int, request: Request,
                   db: Session = Depends(get_db), 
                   current_user: models.AdminUser = Depends(get_current_user)):

    media_item = db.query(models.MediaAsset).filter(models.MediaAsset.id == id).first()
    if not media_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")

    # Get client IP (simplified)
    client_host = request.client.host

    view_log = models.MediaViewLog(
        media_id=id,
        viewed_by_ip=client_host,
        timestamp=datetime.utcnow()
    )
    db.add(view_log)
    db.commit()
    return {"message": f"View logged for media {id} from IP {client_host}"}

# -------------------------
# Get Media Analytics (Authenticated)
# -------------------------
@router.get("/{id}/analytics", response_model=schemas.MediaAnalyticsResponse)
def get_media_analytics(id: int,
                        db: Session = Depends(get_db), 
                        current_user: models.AdminUser = Depends(get_current_user)):

    media_item = db.query(models.MediaAsset).filter(models.MediaAsset.id == id).first()
    if not media_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")

    # Fetch all views for this media
    views = db.query(models.MediaViewLog).filter(models.MediaViewLog.media_id == id).all()

    total_views = len(views)
    unique_ips = len(set(view.viewed_by_ip for view in views))

    # Aggregate views per day
    views_per_day = defaultdict(int)
    for view in views:
        day = view.timestamp.date().isoformat()
        views_per_day[day] += 1

    return {
        "total_views": total_views,
        "unique_ips": unique_ips,
        "views_per_day": dict(views_per_day)
    }
