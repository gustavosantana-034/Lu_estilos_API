import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def test_client_data():
    """Test client data"""
    return {
        "name": "Test Client",
        "email": "client@example.com",
        "cpf": "123.456.789-09",
        "phone": "(11) 98765-4321",
        "address": "Test Address",
        "city": "Test City",
        "state": "TS",
        "postal_code": "12345-678",
    }

def test_create_client(client, test_user_token, test_client_data):
    """Test creating a client"""
    response = client.post(
        "/clients/",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json=test_client_data,
    )
    
    assert response.status_code == 201
    assert response.json()["name"] == test_client_data["name"]
    assert response.json()["email"] == test_client_data["email"]
    assert "id" in response.json()

def test_create_client_duplicate_email(client, test_user_token, test_client_data):
    """Test creating a client with duplicate email"""
    # Create the first client
    client.post(
        "/clients/",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json=test_client_data,
    )
    
    # Create another client with the same email
    response = client.post(
        "/clients/",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json=test_client_data,
    )
    
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_read_clients(client, test_user_token, test_client_data):
    """Test getting all clients"""
    # Create a client
    client.post(
        "/clients/",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json=test_client_data,
    )
    
    # Get all clients
    response = client.get(
        "/clients/",
        headers={"Authorization": f"Bearer {test_user_token}"},
    )
    
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == test_client_data["name"]

def test_read_client(client, test_user_token, test_client_data):
    """Test getting a specific client"""
    # Create a client
    create_response = client.post(
        "/clients/",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json=test_client_data,
    )
    
    client_id = create_response.json()["id"]
    
    # Get the client
    response = client.get(
        f"/clients/{client_id}",
        headers={"Authorization": f"Bearer {test_user_token}"},
    )
    
    assert response.status_code == 200
    assert response.json()["id"] == client_id
    assert response.json()["name"] == test_client_data["name"]

def test_update_client(client, test_user_token, test_client_data):
    """Test updating a client"""
    # Create a client
    create_response = client.post(
        "/clients/",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json=test_client_data,
    )
    
    client_id = create_response.json()["id"]
    
    # Update the client
    update_data = {
        "name": "Updated Client",
        "address": "Updated Address",
    }
    
    response = client.put(
        f"/clients/{client_id}",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json=update_data,
    )
    
    assert response.status_code == 200
    assert response.json()["id"] == client_id
    assert response.json()["name"] == update_data["name"]
    assert response.json()["address"] == update_data["address"]
    assert response.json()["email"] == test_client_data["email"]  # Unchanged

def test_delete_client(client, test_admin_token, test_client_data):
    """Test deleting a client"""
    # Create a client
    create_response = client.post(
        "/clients/",
        headers={"Authorization": f"Bearer {test_admin_token}"},
        json=test_client_data,
    )
    
    client_id = create_response.json()["id"]
    
    # Delete the client
    response = client.delete(
        f"/clients/{client_id}",
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )
    
    assert response.status_code == 204
    
    # Verify the client is deleted
    response = client.get(
        f"/clients/{client_id}",
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )
    
    assert response.status_code == 404