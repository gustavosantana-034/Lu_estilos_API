from app.api.dependencies.database import Base, engine
from app.db.init_db import User

def main():
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")

if __name__ == "__main__":
    main()
