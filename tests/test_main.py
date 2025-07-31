import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app, get_db
from app.models import Base, User, Calculation

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

def test_register_user(db_session):
    response = client.post(
        "/users/register",
        json={"email": "test@example.com", "password": "testpassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    user_in_db = db_session.query(User).filter(User.email == "test@example.com").first()
    assert user_in_db is not None

def test_login_for_access_token(db_session):
    # First, register a user
    client.post(
        "/users/register",
        json={"email": "testlogin@example.com", "password": "testpassword"},
    )
    # Then, login
    response = client.post(
        "/users/login",
        json={"email": "testlogin@example.com", "password": "testpassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def get_auth_headers():
    client.post(
        "/users/register",
        json={"email": "authuser@example.com", "password": "testpassword"},
    )
    response = client.post(
        "/users/login",
        json={"email": "authuser@example.com", "password": "testpassword"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_calculation(db_session):
    headers = get_auth_headers()
    response = client.post(
        "/calculations/",
        headers=headers,
        json={"name": "addition", "a": 1, "b": 2, "result": 3},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "addition"
    assert data["a"] == 1
    assert data["b"] == 2
    assert data["result"] == 3
    assert "id" in data

def test_read_calculations(db_session):
    headers = get_auth_headers()
    client.post(
        "/calculations/",
        headers=headers,
        json={"name": "addition", "a": 1, "b": 2, "result": 3},
    )
    response = client.get("/calculations/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "addition"

def test_read_calculation(db_session):
    headers = get_auth_headers()
    post_response = client.post(
        "/calculations/",
        headers=headers,
        json={"name": "subtraction", "a": 5, "b": 2, "result": 3},
    )
    calculation_id = post_response.json()["id"]
    response = client.get(f"/calculations/{calculation_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "subtraction"

def test_update_calculation(db_session):
    headers = get_auth_headers()
    post_response = client.post(
        "/calculations/",
        headers=headers,
        json={"name": "multiplication", "a": 3, "b": 4, "result": 12},
    )
    calculation_id = post_response.json()["id"]
    response = client.put(
        f"/calculations/{calculation_id}",
        headers=headers,
        json={"name": "updated multiplication", "a": 3, "b": 5, "result": 15},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "updated multiplication"
    assert data["result"] == 15

def test_delete_calculation(db_session):
    headers = get_auth_headers()
    post_response = client.post(
        "/calculations/",
        headers=headers,
        json={"name": "division", "a": 10, "b": 2, "result": 5},
    )
    calculation_id = post_response.json()["id"]
    response = client.delete(f"/calculations/{calculation_id}", headers=headers)
    assert response.status_code == 200
    # Verify it's deleted
    get_response = client.get(f"/calculations/{calculation_id}", headers=headers)
    assert get_response.status_code == 404
