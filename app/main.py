# from fastapi import FastAPI, Depends, HTTPException
# from sqlalchemy.orm import Session
# from . import models, database, schemas, auth, media

# # Create tables
# models.Base.metadata.create_all(bind=database.engine)

# app = FastAPI()

# @app.post("/auth/signup")
# def signup(user: schemas.AdminUserCreate, db: Session = Depends(auth.get_db)):
#     if db.query(models.AdminUser).filter(models.AdminUser.email == user.email).first():
#         raise HTTPException(status_code=400, detail="Email already registered")
#     hashed_pw = auth.hash_password(user.password)
#     db_user = models.AdminUser(email=user.email, hashed_password=hashed_pw)
#     db.add(db_user)
#     db.commit()
#     return {"message": "User created"}

# @app.post("/auth/login")
# def login(user: schemas.AdminUserLogin, db: Session = Depends(auth.get_db)):
#     db_user = db.query(models.AdminUser).filter(models.AdminUser.email == user.email).first()
#     if not db_user or not auth.verify_password(user.password, db_user.hashed_password):
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     token = auth.create_access_token({"id": db_user.id})
#     return {"token": token}

# app.include_router(media.router, prefix="/media")



from fastapi import FastAPI
from . import models, database, auth, media

# Create tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Media Access & Analytics Platform")

# Include auth routes
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Include media routes
app.include_router(media.router, prefix="/media", tags=["Media"])
