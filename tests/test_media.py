# tests/test_media.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def auth_headers():
    # ensure a user exists + login
    email = f"media_user_{uuid.uuid4().hex[:6]}@example.com"
    password = "pass1234"
    client.post("/auth/signup", json={"email": email, "password": password})
    r = client.post("/auth/login", json={"email": email, "password": password})
    token = r.json()["token"]
    return {"Authorization": f"Bearer {token}"}

def create_media(headers):
    payload = {"title": "Sample", "type": "video", "file_url": "http://example.com/file.mp4"}
    r = client.post("/media/", json=payload, headers=headers)
    assert r.status_code == 200
    return r.json()["id"]

def test_stream_url_and_view_and_analytics():
    headers = auth_headers()
    media_id = create_media(headers)

    # get stream url
    r1 = client.get(f"/media/{media_id}/stream-url", headers=headers)
    assert r1.status_code == 200
    assert "stream_url" in r1.json()

    # log a view
    r2 = client.post(f"/media/{media_id}/view", headers=headers)
    assert r2.status_code == 200

    # analytics (should reflect at least 1 view)
    r3 = client.get(f"/media/{media_id}/analytics", headers=headers)
    assert r3.status_code == 200
    body = r3.json()
    assert body["total_views"] >= 1
    assert body["unique_ips"] >= 1
    assert isinstance(body["views_per_day"], dict)

def test_rate_limit_view():
    headers = auth_headers()
    media_id = create_media(headers)

    # Hit 5 times (allowed)
    for _ in range(5):
        r = client.post(f"/media/{media_id}/view", headers=headers)
        assert r.status_code == 200

    # 6th should be rate-limited (429)
    r6 = client.post(f"/media/{media_id}/view", headers=headers)
    assert r6.status_code == 429
