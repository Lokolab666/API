from pydantic import BaseModel, Field
from typing import Optional

# Student schemas
class StudentBase(BaseModel):
    nombre: str


class StudentCreate(StudentBase):
    nombre: str
    codigo: int
    numero_identificacion: int
    


class StudentUpdate(BaseModel):
    student_id: int = 0
    nombre: Optional[str] = None
    codigo: Optional[int] = Field(None, gt=0)
    numero_identificacion: Optional[int] = None


class Student(StudentBase):
    student_id: int
    nombre: str
    codigo: int
    numero_identificacion: int

    class Config:
        orm_mode = True


# Subject schemas
class SubjectBase(BaseModel):
    nombre: str

class SubjectCreate(SubjectBase):
    nombre: str
    aula: str
    creditos: int
    cupos: int


class SubjectUpdate(BaseModel):
    nombre: str = None
    aula: str = None
    creditos: int = Field(None, gt=0)
    cupos: int = Field(None, ge=0)


class Subject(SubjectBase):
    subject_id: int
    nombre: str
    aula: str
    creditos: int
    cupos: int


    class Config:
        orm_mode = True


# Registration schemas
class RegistrationBase(BaseModel):
    student_id: int
    subject_id: int 


class RegistrationCreate(RegistrationBase):
    pass


class RegistrationUpdate(BaseModel):
    student_id: int = None
    subject_id: int = None


class Registration(RegistrationBase):
    inscripcion_id: int
    student_id: int
    subject_id: int

    class Config:
        orm_mode = True

