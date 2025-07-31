from fastapi.testclient import TestClient
from uuid import uuid4

def test_register_user(client: TestClient):
    unique_username = f"testuser_{uuid4()}"
    unique_email = f"test_{uuid4()}@example.com"
    response = client.post("/users/register", json={"username": unique_username, "email": unique_email, "password": "password123"})
    assert response.status_code == 201
    assert response.json()["username"] == unique_username

def test_login(client: TestClient):
    unique_username = f"loginuser_{uuid4()}"
    unique_email = f"login_{uuid4()}@example.com"
    
    client.post("/users/register", json={"username": unique_username, "email": unique_email, "password": "password123"})
    
    response = client.post("/users/login", data={"username": unique_username, "password": "password123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"