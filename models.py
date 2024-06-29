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
    asignaturas = relationship("Asignatura", back_populates="programa")


class Estudiante(Base):
    __tablename__ = "estudiante"
    estudiante_id = Column(Integer, primary_key=True, index=True)
    estudiante_name = Column(String, nullable=False)
    estudiante_last_name = Column(String, nullable=False)
    estudiante_code = Column(String, nullable=False)
    estudiante_type_doc = Column(String, nullable=False)
    estudiante_document = Column(String, nullable=False)
    estudiante_status = Column(String, nullable=False)
    estudiante_photo = Column(String, nullable=True)
    estudiante_programa_fk = Column(Integer, ForeignKey("programa.programa_id"))
    programa = relationship("Programa", back_populates="estudiantes")
    estudiante_autenticacion_fk = Column(Integer, ForeignKey('autenticacion.aut_id'))
    autenticacion = relationship("Autenticacion", back_populates="estudiante")
    inscripciones = relationship("Inscripcion", back_populates="estudiante")


class Autenticacion(Base):
    __tablename__ = "autenticacion"
    aut_id = Column(Integer, primary_key=True, index=True)
    autenticacion_user = Column(String, nullable=False)
    autenticacion_password = Column(String, nullable=False)
    rol_fk = Column(Integer, ForeignKey('rol.rol_id'))
    rol = relationship("Rol", back_populates="autenticacions")
    estudiante = relationship("Estudiante", back_populates="autenticacion")


class Rol(Base):
    __tablename__ = 'rol'
    rol_id = Column(Integer, primary_key=True)
    nombre = Column(String)
    autenticacions = relationship("Autenticacion", back_populates="rol")


class Inscripcion(Base):
    __tablename__ = "inscripcion"
    inscripcion_id = Column(Integer, primary_key=True, index=True)
    estudiante_fk = Column(Integer, ForeignKey('estudiante.estudiante_id'))
    grupo_fk = Column(Integer, ForeignKey('grupo.grupo_id'))
    estudiante = relationship("Estudiante", back_populates="inscripciones")
    grupo = relationship("Grupo", back_populates="inscripciones")


class Asignatura(Base):
    __tablename__ = "asignatura"
    asignatura_id = Column(Integer, primary_key=True, index=True)
    asignatura_nombre = Column(String, nullable=False)
    programa_fk = Column(Integer, ForeignKey("programa.programa_id"))
    programa = relationship("Programa", back_populates="asignaturas")
    grupos = relationship("Grupo", back_populates="asignatura")


class Grupo(Base):
    __tablename__ = "grupo"
    grupo_id = Column(Integer, primary_key=True, index=True)
    grupo_name = Column(String, nullable=False)
    grupo_classroom = Column(String, nullable=False)
    grupo_credits = Column(Integer, nullable=False)
    grupo_quotas = Column(Integer, nullable=False)
    asignatura_fk = Column(Integer, ForeignKey("asignatura.asignatura_id"))
    asignatura = relationship("Asignatura", back_populates="grupos")
    inscripciones = relationship("Inscripcion", back_populates="grupo")


""" Facultad.programas = relationship("Programa", back_populates="facultad")
Programa.facultad = relationship("Facultad", back_populates="programas")
Programa.estudiantes = relationship("Estudiante", back_populates="programa")
Programa.asignaturas = relationship("Asignatura", back_populates="programa")
Estudiante.programa = relationship("Programa", back_populates="estudiantes")
Estudiante.inscripciones = relationship("Inscripcion", back_populates="estudiante")
Estudiante.autenticacion = relationship("Autenticacion", uselist=False, back_populates="estudiante")
Autenticacion.estudiante = relationship("Estudiante", back_populates="autenticacion")
Inscripcion.estudiante = relationship("Estudiante", back_populates="inscripciones")
Inscripcion.grupo = relationship("Grupo", back_populates="inscripciones")
Asignatura.programa = relationship("Programa", back_populates="asignaturas")
Grupo.asignatura = relationship("Asignatura", back_populates="inscripciones")
Grupo.inscripciones = relationship("Inscripcion", back_populates="grupo") """

Base.metadata.create_all(bind=engine)
