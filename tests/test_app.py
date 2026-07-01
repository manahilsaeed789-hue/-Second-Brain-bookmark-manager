"""Tests for Second Brain bookmark manager."""

import pytest
from fastapi.testclient import TestClient

from app import app
from backend.database import Base, engine, SessionLocal, init_db


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_client(client):
    """Register and login a test user, return authenticated client."""
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
    })
    client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123",
    })
    return client


class TestHealth:
    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestAuth:
    def test_register(self, client):
        response = client.post("/api/auth/register", json={
            "email": "new@example.com",
            "username": "newuser",
            "password": "password123",
        })
        assert response.status_code == 200
        assert response.json()["email"] == "new@example.com"

    def test_login(self, client):
        client.post("/api/auth/register", json={
            "email": "login@example.com",
            "username": "loginuser",
            "password": "password123",
        })
        response = client.post("/api/auth/login", json={
            "email": "login@example.com",
            "password": "password123",
        })
        assert response.status_code == 200
        assert "message" in response.json()

    def test_login_invalid(self, client):
        response = client.post("/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "wrong",
        })
        assert response.status_code == 401

    def test_protected_route_without_auth(self, client):
        response = client.get("/api/bookmarks")
        assert response.status_code == 401


class TestBookmarks:
    def test_create_note(self, auth_client):
        response = auth_client.post("/api/bookmarks/note", json={
            "title": "Test Note",
            "content": "This is a test note about machine learning and neural networks.",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Note"
        assert data["short_summary"] is not None

    def test_list_bookmarks(self, auth_client):
        auth_client.post("/api/bookmarks/note", json={
            "title": "List Test",
            "content": "Content for list test about productivity.",
        })
        response = auth_client.get("/api/bookmarks")
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_create_paste(self, auth_client):
        response = auth_client.post("/api/bookmarks/paste", json={
            "content": "Deep learning is a subset of machine learning using neural networks with multiple layers.",
        })
        assert response.status_code == 200
        assert response.json()["source_type"] == "paste"


class TestSearch:
    def test_semantic_search(self, auth_client):
        auth_client.post("/api/bookmarks/note", json={
            "title": "Focus Techniques",
            "content": "The Pomodoro technique helps improve focus and productivity during deep work sessions.",
        })
        response = auth_client.post("/api/search", json={
            "query": "improving focus and concentration",
            "limit": 5,
        })
        assert response.status_code == 200
        data = response.json()
        assert "results" in data


class TestDashboard:
    def test_dashboard_stats(self, auth_client):
        response = auth_client.get("/api/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "total_bookmarks" in data
        assert "trending_tags" in data

    def test_analytics(self, auth_client):
        response = auth_client.get("/api/analytics")
        assert response.status_code == 200
        data = response.json()
        assert "weekly_insights" in data

    def test_collections(self, auth_client):
        response = auth_client.get("/api/collections")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
