import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities

# Initial activities data for resetting
INITIAL_ACTIVITIES = copy.deepcopy(activities)

@pytest.fixture
def client():
    """Fixture to provide a test client for the FastAPI app."""
    return TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    """Fixture to reset the activities data before and after each test."""
    # Arrange: Reset to initial state
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))
    yield
    # Cleanup: Reset after test
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))

# Tests for GET /
def test_root_redirect(client):
    """Test the root endpoint redirects to static index.html."""
    # Act
    response = client.get("/")
    
    # Assert
    assert response.status_code == 200  # RedirectResponse in FastAPI returns 200 with location
    assert response.url.path == "/static/index.html"

# Tests for GET /activities
def test_get_activities_success(client):
    """Test retrieving all activities successfully."""
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == len(INITIAL_ACTIVITIES)
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"

# Tests for POST /activities/{activity_name}/signup
def test_signup_success(client):
    """Test successful signup for an activity."""
    # Arrange
    activity_name = "Tennis Club"
    email = "newstudent@mergington.edu"
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]

def test_signup_activity_not_found(client):
    """Test signup for a non-existent activity."""
    # Arrange
    activity_name = "NonExistent Club"
    email = "student@mergington.edu"
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"

def test_signup_already_signed_up(client):
    """Test signup when student is already signed up."""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already in participants
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student is already signed up for this activity"

# Tests for DELETE /activities/{activity_name}/signup
def test_unregister_success(client):
    """Test successful unregistration from an activity."""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    assert email in activities[activity_name]["participants"]
    
    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]

def test_unregister_activity_not_found(client):
    """Test unregistration from a non-existent activity."""
    # Arrange
    activity_name = "NonExistent Club"
    email = "student@mergington.edu"
    
    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"

def test_unregister_not_signed_up(client):
    """Test unregistration when student is not signed up."""
    # Arrange
    activity_name = "Tennis Club"
    email = "student@mergington.edu"
    assert email not in activities[activity_name]["participants"]
    
    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student is not signed up for this activity"