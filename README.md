# Media Access & Analytics Platform

## Overview

This project is a backend microservice for managing media (audio/video) uploads, secure streaming, and analytics. It simulates real-world backend challenges like authentication, secure access, and data aggregation.

---

## Features

 **User Authentication**: Admin users can sign up and log in via JWT-based authentication.
 **Media Management**: Upload media metadata and generate secure stream URLs.
 **Analytics**: Track who views media, when, and from where (future tasks).
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

 `POST /auth/signup` → Create a new admin user
 `POST /auth/login` → Login and get JWT token

### Media

 `POST /media/media/` → Add media metadata (authenticated)
 `GET /media/media/{id}/stream-url` → Get secure streaming URL

---

## Setup Instructions

1. Clone the repository:

   ```bash
   git clone <your-repo-url>
   cd <repo-folder>

2. Create a virtual environment:

    python -m venv venv

3. Activate the environment:

    source venv/bin/activate  ## Linux/Mac
    venv\Scripts\activate     ## Windows

4. Install dependencies:

    pip install -r requirements.txt

5. Run the server:

    uvicorn main:app --reload

6. Testing:

    pytest

## Notes & Pro Tips

JWT Security: Keep your secret keys safe and never commit them to GitHub. Use .env files for sensitive data.

API Documentation: FastAPI provides auto-generated docs at /docs and /redoc.

Error Handling: Ensure proper error responses for missing media or invalid tokens.

Analytics: Future tasks involve logging IPs and timestamps for media views.

Professional Documentation: Clear READMEs and proper code comments make your project stand out.

Version Control: Commit small, logical changes and push frequently to GitHub for easy tracking.

---

## Submission Note

This project has been completed as part of the Media Access & Analytics Platform simulation. All tasks for Step 1 have been implemented, tested, and verified. The GitHub repository link has been submitted as the official deliverable.
