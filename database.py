# The database setup, including connection details and session management.
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
#TODO: Configue the username and password of the SQL Server
DATABASE_URL = "mssql+pyodbc://username:password@server/dbname?driver=SQL+Server"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
