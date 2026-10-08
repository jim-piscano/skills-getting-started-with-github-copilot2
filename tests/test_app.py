from fastapi.testclient import TestClient
import pytest

from src import app as app_module


@pytest.fixture
def activities(monkeypatch):
    test_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["student@example.com"],
        }
    }
    monkeypatch.setattr(app_module, "activities", test_activities)
    return test_activities


@pytest.fixture
def client():
    return TestClient(app_module.app)


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_current_activities(client, activities):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == activities


def test_signup_adds_student_to_activity(client, activities):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "new-student@example.com"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up new-student@example.com for Chess Club"
    }
    assert activities["Chess Club"]["participants"] == [
        "student@example.com",
        "new-student@example.com",
    ]


def test_signup_returns_not_found_for_unknown_activity(client, activities):
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
