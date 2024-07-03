from pydantic import BaseModel, Field
from typing import Optional
from fastapi import UploadFile, File

# Student schemas
class StudentBase(BaseModel):
    estudiante_id: int
    estudiante_name: str
    estudiante_last_name: str
    estudiante_code: str
    estudiante_type_doc: str
    estudiante_document: str
    estudiante_status: str
    estudiante_photo: Optional[str] = None
    estudiante_programa_fk: int
    estudiante_autenticacion_fk: int


class StudentCreate(StudentBase):
    estudiante_id: Optional[int] = None
    estudiante_name: Optional[str] = None
    estudiante_last_name: Optional[str] = None
    estudiante_code: Optional[str] = None
    estudiante_type_doc: Optional[str] = None
    estudiante_document: Optional[str] = None
    estudiante_status: Optional[str] = None
    estudiante_programa_fk: Optional[int] = None
    estudiante_autenticacion_fk: Optional[int] = None
    

class StudentUpdate(BaseModel):
    estudiante_name: Optional[str] = None
    estudiante_last_name: Optional[str] = None
    estudiante_type_doc: Optional[str] = None
    estudiante_status: Optional[str] = None
    estudiante_photo: Optional[UploadFile] = File(None)


class Student(StudentBase):
    estudiante_id: int
    estudiante_name: str
    estudiante_last_name: str
    estudiante_code: str
    estudiante_type_doc: str
    estudiante_document: str
    estudiante_status: str
    estudiante_photo: str
    estudiante_programa_fk: int
    estudiante_autenticacion_fk: int

    class Config:
        orm_mode = True


# Subject schemas
class SubjectBase(BaseModel):
    asignatura_id: int
    asignatura_nombre: str
    programa_fk: int


class SubjectCreate(SubjectBase):
    asignatura_nombre: Optional[str] = None
    programa_fk: Optional[int] = None


class SubjectUpdate(BaseModel):
    asignatura_nombre: Optional[str] = None

    

class Subject(SubjectBase):
    asignatura_id: int
    asignatura_nombre: str
    programa_fk: int


    class Config:
        orm_mode = True


# Grupo schemas
class GroupBase(BaseModel):
    grupo_id: int
    grupo_name: str
    grupo_classroom: str
    grupo_credits: int
    grupo_quotas: int
    asignatura_fk: int


class GroupCreate(GroupBase):
    grupo_id: Optional[int] = None
    grupo_name: Optional[str] = None
    grupo_classroom: Optional[str] = None
    grupo_credits: Optional[int] = None
    grupo_quotas: Optional[int] = None
    asignatura_fk: Optional[int] = None


class GroupUpdate(BaseModel):
    grupo_name: Optional[str] = None
    grupo_classroom: Optional[str] = None
    grupo_credits: int = Field(None, gt=0)
    grupo_quotas: int = Field(None, ge=0)


class Group(GroupBase):
    grupo_id: int
    grupo_name: str
    grupo_classroom: str
    grupo_credits: int
    grupo_quotas: int
    asignatura_fk: int

    class Config:
        orm_mode = True


# Registration schemas
class InscriptionBase(BaseModel):
    inscripcion_id: int
    estudiante_fk: int
    grupo_fk: int 


class InscriptionCreate(InscriptionBase):
    inscripcion_id: Optional[int] = None
    estudiante_fk: Optional[int] = None
    grupo_fk: Optional[int] = None


class InscriptionUpdate(BaseModel):
    estudiante_fk: Optional[int] = None
    grupo_fk: Optional[int] = None


class Inscription(InscriptionBase):
    inscripcion_id: int
    estudiante_fk: int
    grupo_fk: int

    class Config:
        orm_mode = True


# Facultad schemas
class FacultadBase(BaseModel):
    facultad_id: int
    facultad_name: str


class FacultadCreate(FacultadBase):
    facultad_id: Optional[int] = None
    facultad_name: Optional[str] = None


class FacultadUpdate(BaseModel):
    facultad_name: Optional[str] = None


class Facultad(FacultadBase):
    facultad_id: int
    facultad_name: str

    class Config:
        orm_mode = True

# Programa schemas
class ProgramaBase(BaseModel):
    programa_id: int
    programa_name: str
    facultad_fk: int


class ProgramaCreate(ProgramaBase):
    programa_id: Optional[int] = None
    programa_name: Optional[str] = None
    facultad_fk: Optional[int] = None


class ProgramaUpdate(ProgramaBase):
    programa_name: Optional[str] = None
    facultad_fk: Optional[int] = None


class Programa(ProgramaBase):
    programa_id: int
    programa_name: str
    facultad_fk: int

    class Config:
        orm_mode = True

# Autenticacion schemas

class Login(BaseModel):
    autenticacion_user: str
    autenticacion_password: str

class AutenticacionBase(BaseModel):
    aut_id: int
    autenticacion_user: str
    autenticacion_password: str
    rol_fk: int


class AutenticacionCreate(AutenticacionBase):
    aut_id: Optional[int] = None
    autenticacion_user: Optional[str] = None
    autenticacion_password: Optional[str] = None
    rol_fk: Optional[int] = None


class AutenticacionUpdate(AutenticacionBase):
    autenticacion_user: Optional[str] = None
    autenticacion_password: Optional[str] = None
    rol_fk: Optional[int] = None


class Autenticacion(AutenticacionBase):
    aut_id: int
    autenticacion_user: str
    autenticacion_password: str
    rol_fk: int

    class Config:
        orm_mode = True


# Rol schemas

class RolBase(BaseModel):
    rol_id: int
    nombre: str


class RolCreate(RolBase):
    rol_id: Optional[int] = None
    nombre: Optional[str] = None


class RolUpdate(RolBase):
    nombre: Optional[str] = None


class Rol(RolBase):
    rol_id: int
    nombre: str

    class Config:
        orm_mode = True


