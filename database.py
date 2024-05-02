# The database setup, including connection details and session management.
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


server = "simulacion2024.database.windows.net"
dbname = "Estudiantes"  
username = "Karen"
password = "Simulacion2024."


DATABASE_URL = f"mssql+pyodbc://{username}:{password}@{server}/{dbname}?driver=ODBC+Driver+17+for+SQL+Server"


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()

