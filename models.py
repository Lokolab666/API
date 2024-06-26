from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

server = "34.72.89.63"
dbname = "Estudiantes2024"
username = "sqlserver"
password = "Simulacion2024"

DATABASE_URL = f"mssql+pyodbc://{username}:{password}@{server}/{dbname}?driver=ODBC+Driver+17+for+SQL+Server"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Facultad(Base):
    __tablename__ = "facultad"
    facultad_id = Column(Integer, primary_key=True, index=True)
    facultad_name = Column(String, nullable=False)
    programas = relationship("Programa", back_populates="facultad")

class Programa(Base):
    __tablename__ = "programa"
    programa_id = Column(Integer, primary_key=True, index=True)
    programa_name = Column(String, nullable=False)
    facultad_fk = Column(Integer, ForeignKey("facultad.facultad_id"))
    facultad = relationship("Facultad", back_populates="programas")
    estudiantes = relationship("Estudiante", back_populates="programa")
    subjects = relationship("Subject", back_populates="programa")

class Estudiante(Base):
    __tablename__ = "students"
    estudiante_id = Column(Integer, primary_key=True, index=True)
    estudiante_name = Column(String, nullable=False)
    estudiante_last_name = Column(String, nullable=False)
    estudiante_code = Column(String, nullable=False)
    estudiante_type_doc = Column(String, nullable=False)
    estudiante_document = Column(String, nullable=False)
    estudiante_status = Column(String, nullable=False)
    estudiante_photo = Column(LargeBinary, nullable=True)
    estudiante_programa_fk = Column(Integer, ForeignKey("programa.programa_id"))
    programa = relationship("Programa", back_populates="estudiantes")
    registrations = relationship("Inscripcion", back_populates="student")
    autenticacion = relationship("Autenticacion", uselist=False, back_populates="estudiante")

class Autenticacion(Base):
    __tablename__ = "autenticacion"
    aut_id = Column(Integer, primary_key=True, index=True)
    autenticacion_user = Column(String, nullable=False)
    autenticacion_password = Column(String, nullable=False)
    estudiante_fk = Column(Integer, ForeignKey("students.estudiante_id"))
    estudiante = relationship("Estudiante", back_populates="autenticacion")

class Inscripcion(Base):
    __tablename__ = "registrations"
    inscripcion_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('students.estudiante_id'))  
    student = relationship("Estudiante", back_populates="registrations")
    grupo_id = Column(Integer, ForeignKey('grupo.grupo_id'))
    grupo = relationship("Grupo", back_populates="inscripciones")

class Subject(Base):
    __tablename__ = "subjects"
    subject_id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    aula = Column(String, nullable=False)
    creditos = Column(Integer, nullable=False)
    cupos = Column(Integer, nullable=False)
    programa_fk = Column(Integer, ForeignKey("programa.programa_id"))
    programa = relationship("Programa", back_populates="subjects")
    registrations = relationship("Inscripcion", back_populates="subject")

    def create_new_instance(self, db):
        if self.cont >= self.cupos:
            new_instance = Subject(
                nombre=f"{self.nombre} 2.0",
                aula=self.aula,
                creditos=self.creditos,
                cupos=self.cupos
            )
            db.add(new_instance)
            db.commit()
            db.refresh(new_instance)
            return new_instance
        return None 

class Grupo(Base):
    __tablename__ = "grupo"
    grupo_id = Column(Integer, primary_key=True, index=True)
    grupo_name = Column(String, nullable=False)
    grupo_classroom = Column(String, nullable=False)
    grupo_credits = Column(Integer, nullable=False)
    grupo_quotas = Column(Integer, nullable=False)
    subject_fk = Column(Integer, ForeignKey("subjects.subject_id"))
    subject = relationship("Subject", back_populates="registrations")
    inscripciones = relationship("Inscripcion", back_populates="grupo")


Facultad.programas = relationship("Programa", back_populates="facultad")
Programa.facultad = relationship("Facultad", back_populates="programas")
Programa.estudiantes = relationship("Estudiante", back_populates="programa")
Programa.subjects = relationship("Subject", back_populates="programa")
Estudiante.programa = relationship("Programa", back_populates="estudiantes")
Estudiante.registrations = relationship("Inscripcion", back_populates="student")
Estudiante.autenticacion = relationship("Autenticacion", uselist=False, back_populates="estudiante")
Autenticacion.estudiante = relationship("Estudiante", back_populates="autenticacion")
Inscripcion.student = relationship("Estudiante", back_populates="registrations")
Inscripcion.grupo = relationship("Grupo", back_populates="inscripciones")
Subject.programa = relationship("Programa", back_populates="subjects")
Subject.registrations = relationship("Inscripcion", back_populates="subject")
Grupo.subject = relationship("Subject", back_populates="registrations")
Grupo.inscripciones = relationship("Inscripcion", back_populates="grupo")

Base.metadata.create_all(bind=engine)
