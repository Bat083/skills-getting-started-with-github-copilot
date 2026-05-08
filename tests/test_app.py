"""
Backend tests for the Mergington High School Activities API
Using the AAA (Arrange-Act-Assert) testing pattern
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


class TestGetActivities:
    """Test GET /activities endpoint"""

    def test_get_activities_success(self, client):
        """Test retrieving all activities successfully"""
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        for activity_name in expected_activities:
            assert activity_name in activities
            activity = activities[activity_name]
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)


class TestSignupForActivity:
    """Test POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client):
        """Test successfully signing up for an activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "test.student@mergington.edu"
        initial_response = client.get(f"/activities")
        initial_participants = initial_response.json()[activity_name]["participants"].copy()

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert email in result["message"]
        assert activity_name in result["message"]
        
        # Verify participant was added
        updated_response = client.get("/activities")
        updated_participants = updated_response.json()[activity_name]["participants"]
        assert email in updated_participants
        assert len(updated_participants) == len(initial_participants) + 1

    def test_signup_activity_not_found(self, client):
        """Test signing up for a non-existent activity"""
        # Arrange
        activity_name = "Non-Existent Activity"
        email = "test.student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "Activity not found" in result["detail"]


class TestUnregisterFromActivity:
    """Test DELETE /activities/{activity_name}/signup endpoint"""

    def test_unregister_success(self, client):
        """Test successfully unregistering from an activity"""
        # Arrange
        activity_name = "Chess Club"
        # Get an existing participant
        activities_response = client.get("/activities")
        existing_participants = activities_response.json()[activity_name]["participants"]
        email = existing_participants[0]
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert email in result["message"]
        assert activity_name in result["message"]
        
        # Verify participant was removed
        updated_response = client.get("/activities")
        updated_participants = updated_response.json()[activity_name]["participants"]
        assert email not in updated_participants

    def test_unregister_activity_not_found(self, client):
        """Test unregistering from a non-existent activity"""
        # Arrange
        activity_name = "Non-Existent Activity"
        email = "test.student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "Activity not found" in result["detail"]

    def test_unregister_student_not_registered(self, client):
        """Test unregistering when student is not registered for the activity"""
        # Arrange
        activity_name = "Programming Class"
        email = "not.registered@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "Student not registered" in result["detail"]
