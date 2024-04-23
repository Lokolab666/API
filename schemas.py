from pydantic import BaseModel

class CourseBase(BaseModel):
    title: str

class CourseCreate(CourseBase):
    pass

class Course(CourseBase):
    id: int
    class Config:
        orm_mode = True

class StudentBase(BaseModel):
    name: str

class StudentCreate(StudentBase):
    pass

class Student(StudentBase):
    id: int
    class Config:
        orm_mode = True

class InscriptionBase(BaseModel):
    course_id: int
    student_id: int

class InscriptionCreate(InscriptionBase):
    pass

class Inscription(InscriptionBase):
    id: int
    class Config:
        orm_mode = True
