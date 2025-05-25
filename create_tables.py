from app.api.dependencies.database import Base, engine
from app.db.init_db import User
from app.models.client import Client 

def main():
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    main()
