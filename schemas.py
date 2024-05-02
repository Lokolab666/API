from pydantic import BaseModel, Field

# Student schemas
class StudentBase(BaseModel):
    nombre: str


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    nombre: str = None
    codigo: int = Field(None, gt=0)
    numero_identificacion: int = None


class Student(StudentBase):
    estudiante_id: int
    codigo: int
    numero_identificacion: int

    class Config:
        orm_mode = True


# Subject schemas
class SubjectBase(BaseModel):
    materia_id: int
    nombre: str
    aula: str
    creditos: int
    cupos: int


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    nombre: str = None
    aula: str = None
    creditos: int = Field(None, gt=0)
    cupos: int = Field(None, ge=0)


class Subject(SubjectBase):
    materia_id: int

    class Config:
        orm_mode = True


# Registration schemas
class RegistrationBase(BaseModel):
    estudiante_id: int
    materia_id: int 


class RegistrationCreate(RegistrationBase):
    pass


class RegistrationUpdate(BaseModel):
    estudiante_id: int = None
    materia_id: int = None


class Registration(RegistrationBase):
    inscripcion_id: int

    class Config:
        orm_mode = True

