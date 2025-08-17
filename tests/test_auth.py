# tests/auth_test.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_signup_and_login():
    # unique email each run
    import uuid
    email = f"user_test_{uuid.uuid4().hex[:6]}@example.com"
    password = "pass1234"

    r1 = client.post("/auth/signup", json={"email": email, "password": password})
    assert r1.status_code in (200, 400)  # may be 400 if re-running

    r2 = client.post("/auth/login", json={"email": email, "password": password})
    assert r2.status_code == 200
    token = r2.json().get("token")
    assert token
