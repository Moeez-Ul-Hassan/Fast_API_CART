from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Connects to your local XAMPP MySQL 'cart' database
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:@localhost:3306/cart"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()