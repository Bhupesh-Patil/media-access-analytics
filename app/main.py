# app/main.py
from fastapi import FastAPI
from . import models, database, auth, media
import os
from dotenv import load_dotenv

load_dotenv()

# Create tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Media Access & Analytics Platform")

# Check Redis availability
try:
    import redis as redis_py
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))
    rclient = redis_py.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
    rclient.ping()
    app.state.redis_available = True
except Exception:
    app.state.redis_available = False

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(media.router, prefix="/media", tags=["Media"])

# ✅ Root route for testing
@app.get("/")
async def root():
    return {"message": "Welcome to Media Access & Analytics Platform"}
