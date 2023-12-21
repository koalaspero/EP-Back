from sqlalchemy import create_engine, MetaData
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Configura tu conexión a la base de datos
DATABASE_URL = "mysql+pymysql://root@localhost:3306/ep_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
