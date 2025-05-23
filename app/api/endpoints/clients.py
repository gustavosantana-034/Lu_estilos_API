from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_db
from app.core.security import get_current_active_user, get_current_admin_user
from app.models.client import Client
from app.models.user import User
from app.schemas.client import ClientCreate, ClientUpdate, Client as ClientSchema

router = APIRouter()

@router.get("/", response_model=List[ClientSchema])
async def read_clients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    email: Optional[str] = None,
):
    """
    Retrieve clients with pagination and filtering options
    """
    query = db.query(Client)
    
    # Apply filters if provided
    if name:
        query = query.filter(Client.name.ilike(f"%{name}%"))
    if email:
        query = query.filter(Client.email.ilike(f"%{email}%"))
    
    # Get paginated results
    clients = query.offset(skip).limit(limit).all()
    
    return clients

@router.post("/", response_model=ClientSchema, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_in: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new client
    """
    # Check if client with this email already exists
    if db.query(Client).filter(Client.email == client_in.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Check if client with this CPF already exists
    # First, remove formatting from CPF to compare correctly
    cpf_digits = ''.join(filter(str.isdigit, client_in.cpf))
    existing_clients = db.query(Client).all()
    
    for existing_client in existing_clients:
        existing_cpf_digits = ''.join(filter(str.isdigit, existing_client.cpf))
        if existing_cpf_digits == cpf_digits:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF already registered",
            )
    
    # Create new client
    db_client = Client(
        name=client_in.name,
        email=client_in.email,
        cpf=client_in.cpf,
        phone=client_in.phone,
        address=client_in.address,
        city=client_in.city,
        state=client_in.state,
        postal_code=client_in.postal_code,
        is_active=client_in.is_active,
        created_by=current_user.id,
    )
    
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    
    return db_client

@router.get("/{client_id}", response_model=ClientSchema)
async def read_client(
    client_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific client by ID
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )
    
    return client

@router.put("/{client_id}", response_model=ClientSchema)
async def update_client(
    client_id: str,
    client_in: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a client
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )
    
    # Check email uniqueness if updating email
    if client_in.email and client_in.email != client.email:
        if db.query(Client).filter(Client.email == client_in.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
    
    # Update client fields
    update_data = client_in.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(client, field, value)
    
    db.add(client)
    db.commit()
    db.refresh(client)
    
    return client

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),  # Only admins can delete
):
    """
    Delete a client
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )
    
    db.delete(client)
    db.commit()
    
    return None