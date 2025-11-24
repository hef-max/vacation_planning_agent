# tests/conftest.py
"""
Pytest configuration and fixtures.
"""
import pytest
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# Test database
TEST_DATABASE_URL = "sqlite:///./test_vacation_planner.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    """Override database dependency for testing."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override the dependency
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def client():
    """Create test client with fresh database."""
    # Create tables
    Base.metadata.create_all(bind=test_engine)
    
    with TestClient(app) as c:
        yield c
    
    # Cleanup
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def db_session():
    """Create database session for direct DB access in tests."""
    Base.metadata.create_all(bind=test_engine)
    session = TestSessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def sample_plan_request():
    """Sample plan request data."""
    return {
        "user_id": "test_user",
        "destination": "Yogyakarta",
        "start_date": "2025-12-20",
        "end_date": "2025-12-24",
        "budget_idr": 5000000,
        "travel_type": "culture",
        "travelers": 2,
        "preferences": "prefer homestay and local food"
    }

@pytest.fixture
def sample_booking_confirm():
    """Sample booking confirmation data."""
    return {
        "plan_id": "plan_test123",
        "user_id": "test_user",
        "payment_token": "tok_valid_test123",
        "confirmed": True
    }