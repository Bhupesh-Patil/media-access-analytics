# Media Access & Analytics Platform

## Overview

This project is a backend microservice for managing media (audio/video) uploads, secure streaming, and analytics. It simulates real-world backend challenges like authentication, secure access, and data aggregation.

---

## Features

 **User Authentication**: Admin users can sign up and log in via JWT-based authentication.
 **Media Management**: Upload media metadata and generate secure stream URLs.
 **Analytics**: Track who views media, when, and from where. Provides:

- Total views per media
- Unique IP count
- Daily views breakdown
 **Secure Routes**: All protected routes require a valid JWT token.

---

## Technologies

 **Backend**: Python, FastAPI
 **Database**: SQLite / PostgreSQL (adjust as per setup)
 **Authentication**: JWT
 **Testing**: pytest, FastAPI TestClient

---

## Database Models

 **AdminUser**: `id`, `email`, `hashed_password`, `created_at`
 **MediaAsset**: `id`, `title`, `type`, `file_url`, `created_at`
 **MediaViewLog**: `media_id`, `viewed_by_ip`, `timestamp`

---

## APIs

### Authentication

-`POST /auth/signup` → Create a new admin user
-`POST /auth/login` → Login and get JWT token

### Media

-`POST /media/` → Add media metadata (authenticated)  
-`GET /media/{id}/stream-url` → Get secure streaming URL (authenticated)  
-`POST /media/{id}/view` → Log a media view (authenticated)  
-`GET /media/{id}/analytics` → Get analytics for a media (authenticated)

---

## API Endpoints

| Method | Endpoint | Description | Example Request | Example Response |
|--------|----------|-------------|-----------------|----------------|
| POST | `/auth/signup` | Create a new admin user | `{ "email": "admin@example.com", "password": "pass123" }` | `{ "message": "User created" }` |
| POST | `/auth/login` | Login and get JWT token | `{ "email": "admin@example.com", "password": "pass123" }` | `{ "token": "eyJhbGciOiJIUzI..." }` |
| POST | `/media/` | Add media metadata (authenticated) | `{ "title": "Sample Media", "type": "video", "file_url": "http://example.com/sample.mp4" }` | `{ "id": 1, "title": "Sample Media", "type": "video", "file_url": "http://example.com/sample.mp4" }` |
| GET | `/media/{id}/stream-url` | Get secure streaming URL (authenticated) | - | `{ "stream_url": "http://example.com/sample.mp4" }` |
| POST | `/media/{id}/view` | Log a media view (authenticated) | - | `{ "message": "View logged for media 1 from IP 127.0.0.1" }` |
| GET | `/media/{id}/analytics` | Get media analytics (authenticated) | - | `{ "total_views": 1, "unique_ips": 1, "views_per_day": { "2025-08-15": 1 } }` |

---

## Setup Instructions

1. Clone the repository:

   ```bash
   git clone <your-repo-url>
   cd <repo-folder>

2. Create a virtual environment:

    ```bash
    python -m venv venv

3. Activate the environment:

    ```bash
    source venv/bin/activate  ## Linux/Mac
    venv\Scripts\activate     ## Windows

4. Install dependencies:

    ```bash
    pip install -r requirements.txt

5. Run the server:

    ```bash
    uvicorn main:app --reload

6. Testing:

    ```bash
    pytest

---

## Notes & Pro Tips

**JWT Security**: Keep your secret keys safe and never commit them to GitHub. Use `.env` files for sensitive data.  
**API Documentation**: FastAPI provides auto-generated docs at `/docs` and `/redoc`.  
**Error Handling**: Ensure proper error responses for missing media, invalid tokens, or other edge cases.  
**Analytics & JWT Security**:  

- All media routes require a valid JWT token.  
- `POST /media/{id}/view` logs the viewer's IP and timestamp.  
- `GET /media/{id}/analytics` returns total views, unique IPs, and daily breakdown.  
**Professional Documentation**: Clear READMEs and proper code comments make your project stand out.  
**Version Control**: Commit small, logical changes and push frequently to GitHub for easy tracking.  
**Testing**: Use FastAPI TestClient or Swagger UI to verify all endpoints after any update.  

---

## Submission Note

This project has completed Task 2: Media access logging and analytics with JWT-secured endpoints. All features have been tested with FastAPI docs and verified.
