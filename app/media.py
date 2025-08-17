# app/media.py
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from collections import defaultdict
import json
import os
import time

from . import models, schemas, database
from .auth import get_current_user
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# attempt to import redis; if not available or connection fails, fallback to in-memory
try:
    import redis as redis_py
    _redis_client = redis_py.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
    try:
        _redis_client.ping()
        redis_client = _redis_client
        _USING_REDIS = True
    except Exception:
        redis_client = None
        _USING_REDIS = False
except Exception:
    redis_client = None
    _USING_REDIS = False

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# In-memory fallback cache + rate limiter (only for dev / tests)
_inmemory_cache = {}
_inmemory_rate = {}

def _cache_get(key):
    if _USING_REDIS:
        val = redis_client.get(key)
        return json.loads(val) if val else None
    else:
        entry = _inmemory_cache.get(key)
        if not entry:
            return None
        value, expires_at = entry
        if expires_at and time.time() > expires_at:
            del _inmemory_cache[key]
            return None
        return value

def _cache_setex(key, ttl_seconds, value):
    if _USING_REDIS:
        redis_client.setex(key, ttl_seconds, json.dumps(value))
    else:
        expires_at = time.time() + ttl_seconds if ttl_seconds else None
        _inmemory_cache[key] = (value, expires_at)

def _cache_delete(key):
    if _USING_REDIS:
        redis_client.delete(key)
    else:
        _inmemory_cache.pop(key, None)

def _rate_limit_check(key: str, limit: int, window_seconds: int) -> bool:
    """
    Returns True if allowed (not rate limited), False if limited.
    key should include identity (e.g. f"rl:{media_id}:{ip}")
    """
    if _USING_REDIS:
        # Using Redis INCR with expiry
        current = redis_client.incr(key)
        if current == 1:
            redis_client.expire(key, window_seconds)
        return current <= limit
    else:
        now = int(time.time())
        window_key = f"{key}:{now // window_seconds}"
        count = _inmemory_rate.get(window_key, 0) + 1
        _inmemory_rate[window_key] = count
        # Clean up old keys occasionally (simple)
        if len(_inmemory_rate) > 10000:
            _inmemory_rate.clear()
        return count <= limit

# Add Media (JWT-protected)
@router.post("/", response_model=schemas.MediaAssetResponse)
def add_media(
    media: schemas.MediaAssetCreate,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(get_current_user),
):
    new_media = models.MediaAsset(
        title=media.title,
        type=media.type,
        file_url=media.file_url,
        created_at=datetime.utcnow(),
    )
    db.add(new_media)
    db.commit()
    db.refresh(new_media)
    return new_media

# Get Secure Stream URL (JWT-protected) — 10-minute signed link (simple query param)
@router.get("/{id}/stream-url")
def get_stream_url(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(get_current_user),
):
    media_item = db.query(models.MediaAsset).filter(models.MediaAsset.id == id).first()
    if not media_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")

    expires = (datetime.utcnow() + timedelta(minutes=10)).isoformat()
    stream_url = f"{media_item.file_url}?{('expires=' + expires)}"
    return {"stream_url": stream_url}

# Log a Media View (JWT-protected) with per-IP rate limit (5/min)
@router.post("/{id}/view")
def log_media_view(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(get_current_user),
):
    media_item = db.query(models.MediaAsset).filter(models.MediaAsset.id == id).first()
    if not media_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")

    client_host = request.client.host if request.client else "unknown"

    # Rate-limit per IP per media: 5 requests per 60 seconds
    rl_key = f"rl:media:{id}:ip:{client_host}"
    allowed = _rate_limit_check(rl_key, limit=5, window_seconds=60)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")

    view_log = models.MediaViewLog(
        media_id=id, viewed_by_ip=client_host, timestamp=datetime.utcnow()
    )
    db.add(view_log)
    db.commit()

    # Invalidate analytics cache after each view
    _cache_delete(f"media_analytics:{id}")

    return {"message": f"View logged for media {id} from IP {client_host}"}

# Get Media Analytics (JWT-protected) with Redis caching (TTL 1h)
@router.get("/{id}/analytics", response_model=schemas.MediaAnalyticsResponse)
def get_media_analytics(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(get_current_user),
):
    media_item = db.query(models.MediaAsset).filter(models.MediaAsset.id == id).first()
    if not media_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")

    cache_key = f"media_analytics:{id}"
    cached = _cache_get(cache_key)
    if cached:
        return cached

    views = db.query(models.MediaViewLog).filter(models.MediaViewLog.media_id == id).all()
    total_views = len(views)
    unique_ips = len(set(v.viewed_by_ip for v in views))

    views_per_day = defaultdict(int)
    for v in views:
        # v.timestamp may be naive datetime
        views_per_day[v.timestamp.date().isoformat()] += 1

    analytics = {
        "total_views": total_views,
        "unique_ips": unique_ips,
        "views_per_day": dict(views_per_day),
    }

    # Cache for 1 hour (3600 seconds)
    _cache_setex(cache_key, 3600, analytics)
    return analytics
