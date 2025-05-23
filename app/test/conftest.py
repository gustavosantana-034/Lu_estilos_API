import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies.database import Base, get_db
from app.main import app
from app.models.user import User
from app.core.security import get_password_hash

# Create a test database in memory
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the tables
Base.metadata.create_all(bind=engine)

@pytest.fixture
def db_session():
    """
    Create a fresh database session for each test
    """
    # Create the tables
    Base.metadata.create_all(bind=engine)
    
    # Create a session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    
    # Drop all tables after the test
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    """
    Create a test client with a database session
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Remove the override
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db_session):
    """
    Create a test user
    """
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User",
        is_active=True,
        is_admin=False,
    )
    
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    return user

@pytest.fixture
def test_admin(db_session):
    """
    Create a test admin user
    """
    admin = User(
        email="admin@example.com",
        username="adminuser",
        hashed_password=get_password_hash("adminpassword"),
        full_name="Admin User",
        is_active=True,
        is_admin=True,
    )
    
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    
    return admin

@pytest.fixture
def test_user_token(client, test_user):
    """
    Create a JWT token for the test user
    """
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "testpassword"},
    )
    
    return response.json()["access_token"]

@pytest.fixture
def test_admin_token(client, test_admin):
    """
    Create a JWT token for the test admin
    """
    response = client.post(
        "/auth/login",
        data={"username": "admin@example.com", "password": "adminpassword"},
    )
    
    return response.json()["access_token"]