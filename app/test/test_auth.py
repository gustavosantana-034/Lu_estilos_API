import pytest
from fastapi.testclient import TestClient

def test_login_success(client, test_user):
    """Test successful login"""
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "testpassword"},
    )
    
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_invalid_credentials(client, test_user):
    """Test login with invalid credentials"""
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "wrongpassword"},
    )
    
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

def test_register_success(client):
    """Test successful user registration"""
    response = client.post(
        "/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "NewPassword123",
            "full_name": "New User",
        },
    )
    
    assert response.status_code == 200
    assert response.json()["email"] == "newuser@example.com"
    assert response.json()["username"] == "newuser"
    assert "id" in response.json()

def test_register_existing_email(client, test_user):
    """Test registration with existing email"""
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "username": "anotheruser",
            "password": "Password123",
            "full_name": "Another User",
        },
    )
    
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_register_existing_username(client, test_user):
    """Test registration with existing username"""
    response = client.post(
        "/auth/register",
        json={
            "email": "another@example.com",
            "username": "testuser",
            "password": "Password123",
            "full_name": "Another User",
        },
    )
    
    assert response.status_code == 400
    assert "Username already taken" in response.json()["detail"]

def test_refresh_token(client, test_user_token):
    """Test token refresh"""
    response = client.post(
        "/auth/refresh-token",
        headers={"Authorization": f"Bearer {test_user_token}"},
    )
    
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_refresh_token_invalid_token(client):
    """Test token refresh with invalid token"""
    response = client.post(
        "/auth/refresh-token",
        headers={"Authorization": "Bearer invalid_token"},
    )
    
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]