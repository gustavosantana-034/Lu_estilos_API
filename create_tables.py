from app.api.dependencies.database import Base, engine
from app.db.init_db import User
from app.models.client import Client 
from app.models.product import Product
from app.models.order import Order

def main():
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    main()
