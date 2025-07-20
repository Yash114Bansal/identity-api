import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Utility to reset DB between tests (for SQLite, not for production)
def reset_db():
    from app.db.session import engine
    from app.models.base import Base
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

@pytest.fixture(autouse=True)
def run_around_tests():
    reset_db()
    yield
    reset_db()

def test_identify_new_contact():
    response = client.post("/identify", json={"email": "test1@example.com", "phoneNumber": "111111"})
    assert response.status_code == 200
    data = response.json()["primaryContatctId"]
    assert data is not None

def test_identify_existing_contact_by_email():
    # Create contact
    client.post("/identify", json={"email": "test2@example.com", "phoneNumber": "222222"})
    # Identify by email only
    response = client.post("/identify", json={"email": "test2@example.com"})
    assert response.status_code == 200
    data = response.json()
    assert data["primaryContatctId"] is not None
    assert "test2@example.com" in data["emails"]
    assert "222222" in data["phoneNumbers"]

def test_identify_existing_contact_by_phone():
    # Create contact
    client.post("/identify", json={"email": "test3@example.com", "phoneNumber": "333333"})
    # Identify by phone only
    response = client.post("/identify", json={"phoneNumber": "333333"})
    assert response.status_code == 200
    data = response.json()
    assert data["primaryContatctId"] is not None
    assert "test3@example.com" in data["emails"]
    assert "333333" in data["phoneNumbers"]

def test_identify_creates_secondary_contact():
    # Create initial contact
    client.post("/identify", json={"email": "test4@example.com", "phoneNumber": "444444"})
    # New info with same phone, new email
    response = client.post("/identify", json={"email": "test4b@example.com", "phoneNumber": "444444"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["secondaryContactIds"]) == 1
    assert "test4b@example.com" in data["emails"]
    assert "test4@example.com" in data["emails"]

def test_identify_merges_primaries():
    # Create two primaries
    client.post("/identify", json={"email": "merge1@example.com", "phoneNumber": "555555"})
    client.post("/identify", json={"email": "merge2@example.com", "phoneNumber": "666666"})
    # Now link them
    response = client.post("/identify", json={"email": "merge1@example.com", "phoneNumber": "666666"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["emails"]) == 2
    assert len(data["phoneNumbers"]) == 2
    assert len(data["secondaryContactIds"]) >= 1

def test_identify_invalid_input():
    response = client.post("/identify", json={})
    assert response.status_code == 422
    assert "Invalid contact input" in response.text
