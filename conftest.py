import pytest
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# This adds the project's root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database import Base
from app.main import app

DATABASE_URL = os.getenv("DATABASE_URL")

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)  # Create tables
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)  # Drop tables

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c