# SQLAlchemy models that correspond to the database tables.
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

server = "simulacion2024.database.windows.net"
dbname = "Estudiantes"  
username = "Karen"
password = "Simulacion2024."

DATABASE_URL = f"mssql+pyodbc://{username}:{password}@{server}/{dbname}?driver=ODBC+Driver+17+for+SQL+Server"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Subject(Base):
    __tablename__ = "subjects"
    subject_id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    aula = Column(String, nullable=False)
    creditos = Column(Integer, nullable=False)
    cupos = Column(Integer, nullable=False)
    cont = Column(Integer, nullable=False)
    registrations = relationship("Registration", back_populates="subject")


    def create_new_instance(self, db):
        if self.cont >= self.cupos:
            new_instance = Subject(
                nombre=f"{self.nombre} 2.0",
                aula=self.aula,
                creditos=self.creditos,
                cupos=self.cupos,
                cont=0  
            )
            db.add(new_instance)
            db.commit()
            db.refresh(new_instance)
            return new_instance
        return None 


class Student(Base):
    __tablename__ = "students"
    student_id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    codigo = Column(Integer, nullable=False)
    numero_identificacion = Column(Integer, nullable=False)
    registrations = relationship("Registration", back_populates="student")


class Registration(Base):
    __tablename__ = "registrations"
    inscripcion_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('students.student_id'))  
    student = relationship("Student", back_populates="registrations")
    subject_id = Column(Integer, ForeignKey('subjects.subject_id'))
    subject = relationship("Subject", back_populates="registrations")
    student = relationship("Student", back_populates="registrations")


Base.metadata.create_all(bind=engine)

