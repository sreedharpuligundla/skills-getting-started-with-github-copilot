"""
Tests for the Mergington High School Activities API

Tests cover:
- Root redirect endpoint
- Getting all activities
- Signing up for activities
- Removing participants from activities
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the API"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original activities
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
            "description": "Competitive basketball team for interscholastic play",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Track and Field": {
            "description": "Running, jumping, and throwing events for all skill levels",
            "schedule": "Tuesdays and Thursdays, 3:45 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["alex@mergington.edu", "maya@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in school plays and develop theatrical skills",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["lucas@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and mixed media techniques",
            "schedule": "Mondays, 3:30 PM - 4:45 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu", "noah@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation and public speaking skills through competitive debate",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["ava@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts through hands-on projects",
            "schedule": "Fridays, 3:30 PM - 4:45 PM",
            "max_participants": 16,
            "participants": ["ethan@mergington.edu", "charlotte@mergington.edu"]
        }
    }
    
    # Clear and restore activities
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static HTML"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for retrieving activities"""
    
    def test_get_all_activities(self, client, reset_activities):
        """Test getting all activities returns all activities with correct structure"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
        
        # Verify Chess Club exists and has correct structure
        assert "Chess Club" in data
        chess_club = data["Chess Club"]
        assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
        assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
        assert chess_club["max_participants"] == 12
        assert isinstance(chess_club["participants"], list)
        assert len(chess_club["participants"]) == 2
    
    def test_activities_have_required_fields(self, client, reset_activities):
        """Test that all activities have required fields"""
        response = client.get("/activities")
        data = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        for activity_name, activity_details in data.items():
            for field in required_fields:
                assert field in activity_details, f"Activity '{activity_name}' missing field '{field}'"


class TestSignupForActivity:
    """Tests for signing up for activities"""
    
    def test_signup_new_participant(self, client, reset_activities):
        """Test successfully signing up a new participant"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_duplicate_participant(self, client, reset_activities):
        """Test that duplicate signup is rejected"""
        # Try to sign up someone already registered
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signing up for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_signup_url_encoded_activity_name(self, client, reset_activities):
        """Test signing up with URL-encoded activity name"""
        # Programming Class needs to be URL-encoded as Programming%20Class
        response = client.post(
            "/activities/Programming%20Class/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Programming Class"]["participants"]
    
    def test_signup_multiple_participants(self, client, reset_activities):
        """Test signing up multiple different participants"""
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        for email in emails:
            response = client.post(
                f"/activities/Drama%20Club/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all participants were added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        drama_club_participants = activities_data["Drama Club"]["participants"]
        
        for email in emails:
            assert email in drama_club_participants


class TestRemoveParticipant:
    """Tests for removing participants from activities"""
    
    def test_remove_existing_participant(self, client, reset_activities):
        """Test successfully removing an existing participant"""
        response = client.delete(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Removed" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
    
    def test_remove_nonexistent_participant(self, client, reset_activities):
        """Test removing a participant who isn't signed up"""
        response = client.delete(
            "/activities/Chess%20Club/signup?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"]
    
    def test_remove_from_nonexistent_activity(self, client, reset_activities):
        """Test removing participant from non-existent activity"""
        response = client.delete(
            "/activities/Fake%20Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_remove_multiple_participants(self, client, reset_activities):
        """Test removing multiple participants from an activity"""
        original_count = len(activities["Track and Field"]["participants"])
        
        # Remove first participant
        response1 = client.delete(
            "/activities/Track%20and%20Field/signup?email=alex@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Remove second participant
        response2 = client.delete(
            "/activities/Track%20and%20Field/signup?email=maya@mergington.edu"
        )
        assert response2.status_code == 200
        
        # Verify both were removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert len(activities_data["Track and Field"]["participants"]) == original_count - 2


class TestIntegration:
    """Integration tests combining multiple operations"""
    
    def test_signup_and_remove_flow(self, client, reset_activities):
        """Test complete flow: signup, verify, remove, verify"""
        email = "testuser@mergington.edu"
        activity = "Art%20Studio"
        
        # Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify signup
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Art Studio"]["participants"]
        original_count = len(activities_data["Art Studio"]["participants"])
        
        # Remove
        remove_response = client.delete(f"/activities/{activity}/signup?email={email}")
        assert remove_response.status_code == 200
        
        # Verify removal
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data["Art Studio"]["participants"]
        assert len(activities_data["Art Studio"]["participants"]) == original_count - 1
    
    def test_concurrent_signups_same_activity(self, client, reset_activities):
        """Test multiple signups for the same activity"""
        activity = "Science%20Club"
        emails = ["user1@mergington.edu", "user2@mergington.edu", "user3@mergington.edu"]
        
        for email in emails:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all were added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        science_club = activities_data["Science Club"]["participants"]
        
        for email in emails:
            assert email in science_club
