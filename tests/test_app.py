"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team and practice sessions",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and participate in matches",
            "schedule": "Tuesdays and Saturdays, 3:00 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["james@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theater productions, acting techniques, and script writing",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "isabella@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, sculpture, and visual arts",
            "schedule": "Mondays and Fridays, 3:30 PM - 4:45 PM",
            "max_participants": 18,
            "participants": ["grace@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore scientific concepts through experiments and projects",
            "schedule": "Wednesdays, 3:30 PM - 4:45 PM",
            "max_participants": 22,
            "participants": ["mia@mergington.edu"]
        }
    }
    
    # Clear current activities
    activities.clear()
    # Restore original state
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static index"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the get activities endpoint"""
    
    def test_get_all_activities(self, client, reset_activities):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Check that we have all activities
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Basketball Team" in data
    
    def test_activity_structure(self, client, reset_activities):
        """Test that activities have correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)
    
    def test_activities_have_participants(self, client, reset_activities):
        """Test that activities have initial participants"""
        response = client.get("/activities")
        data = response.json()
        
        assert len(data["Chess Club"]["participants"]) > 0
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]


class TestSignup:
    """Tests for the signup endpoint"""
    
    def test_signup_new_student(self, client, reset_activities):
        """Test signing up a new student for an activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_duplicate_student(self, client, reset_activities):
        """Test that duplicate signups are rejected"""
        # First signup
        client.post(
            "/activities/Chess Club/signup",
            params={"email": "test@mergington.edu"}
        )
        
        # Duplicate signup should fail
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signing up for a nonexistent activity"""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_already_registered_student(self, client, reset_activities):
        """Test that already registered students cannot sign up again"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]


class TestUnregister:
    """Tests for the unregister endpoint"""
    
    def test_unregister_student(self, client, reset_activities):
        """Test unregistering a student from an activity"""
        # Verify student is signed up
        activities_before = client.get("/activities").json()
        assert "michael@mergington.edu" in activities_before["Chess Club"]["participants"]
        
        # Unregister
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        
        # Verify student was removed
        activities_after = client.get("/activities").json()
        assert "michael@mergington.edu" not in activities_after["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregistering from a nonexistent activity"""
        response = client.post(
            "/activities/Nonexistent Club/unregister",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_not_registered_student(self, client, reset_activities):
        """Test that unregistering a non-registered student fails"""
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "unregistered@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]
    
    def test_unregister_then_signup_again(self, client, reset_activities):
        """Test unregistering and then signing up again"""
        # Unregister
        client.post(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        
        # Sign up again
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        
        # Verify back in list
        activities_data = client.get("/activities").json()
        assert "michael@mergington.edu" in activities_data["Chess Club"]["participants"]


class TestIntegration:
    """Integration tests combining multiple operations"""
    
    def test_complete_workflow(self, client, reset_activities):
        """Test complete workflow: view, signup, unregister"""
        # View activities
        activities_response = client.get("/activities")
        assert activities_response.status_code == 200
        initial_count = len(activities_response.json()["Programming Class"]["participants"])
        
        # Sign up
        signup_response = client.post(
            "/activities/Programming Class/signup",
            params={"email": "workflow@mergington.edu"}
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        check_response = client.get("/activities")
        new_count = len(check_response.json()["Programming Class"]["participants"])
        assert new_count == initial_count + 1
        
        # Unregister
        unregister_response = client.post(
            "/activities/Programming Class/unregister",
            params={"email": "workflow@mergington.edu"}
        )
        assert unregister_response.status_code == 200
        
        # Verify unregister
        final_response = client.get("/activities")
        final_count = len(final_response.json()["Programming Class"]["participants"])
        assert final_count == initial_count
    
    def test_multiple_signups(self, client, reset_activities):
        """Test multiple students signing up for same activity"""
        initial_count = len(activities["Tennis Club"]["participants"])
        
        # Sign up multiple students
        for i in range(3):
            email = f"student{i}@mergington.edu"
            response = client.post(
                "/activities/Tennis Club/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all signed up
        final_data = client.get("/activities").json()
        final_count = len(final_data["Tennis Club"]["participants"])
        assert final_count == initial_count + 3
