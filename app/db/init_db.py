from sqlalchemy.orm import Session
import os

from app.api.dependencies.database import Base, engine
from app.core.security import get_password_hash
from app.models.user import User

def init_db(db: Session) -> None:
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Check if we should create a default admin user
    if os.environ.get("CREATE_DEFAULT_ADMIN", "false").lower() == "true":
        create_default_admin(db)

def create_default_admin(db: Session) -> None:
    """Create a default admin user"""
    # Check if admin already exists
    admin = db.query(User).filter(User.email == "admin@luestilo.com").first()
    if admin:
        return
    
    # Create admin user
    admin_user = User(
        email="admin@luestilo.com",
        username="admin",
        hashed_password=get_password_hash("admin123"),  # Change in production!
        full_name="Admin User",
        is_active=True,
        is_admin=True,
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)