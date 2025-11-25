# bagian database.py ini digunakan untuk kenektivitas ke MySQL database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "mysql+pymysql://user:pass@db-booking:3306/sentracare_booking"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
