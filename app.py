from fastapi import FastAPI, Depends, HTTPException, status, Query, Request
from typing import List, Optional
from sqlalchemy.orm import Session
import models, schemas, crud
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
from models import Estudiante, Subject, Inscripcion
import uvicorn
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from enum import Enum

models.Base.metadata.create_all(bind=engine)

class SortBy(str, Enum):
    student_id = "student_id"
    nombre = "nombre"
    codigo = "codigo"
    numero_identificacion = "numero_identificacion"

class SortBySubject(str, Enum):
    subject_id = "subject_id"
    nombre = "nombre"
    aula = "aula"
    creditos = "creditos"
    cupos = "cupos"


class SortDirection(str, Enum):
    asc = "asc"
    desc = "desc"


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return JSONResponse(
            status_code=404,
            content={"message": "The resource you are looking for does not exist"},
        )
    # Pass other status codes to the default handler
    return await request.app.default_exception_handler(request, exc)


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    raise HTTPException(status_code=404, detail="Item not found")

#Registration Endpoints

@app.post("/registrations/", response_model=schemas.Registration)
def create_registration(registration: schemas.RegistrationCreate, db: Session = Depends(get_db)):
    db_student = crud.get_student(db, registration.student_id)
    db_subject = crud.get_subject(db, registration.subject_id)
    if db_student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    if db_subject is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
    """ if db_subject.cont >= db_subject.cupos:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Subject already full") """
    existing_registration = db.query(Registration).filter(  
        Registration.student_id == registration.student_id,
        Registration.subject_id == registration.subject_id
    ).first()
    
    if existing_registration:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student already registered for this subject")
    
    new_registration = crud.create_registration(db=db, registration=registration)
    # crud.update_subject_counter(db, registration.subject_id)

    # raise HTTPException(status_code=status.HTTP_200_OK, detail="Student OK to register")
    
    return new_registration


@app.get("/registrations/{registration_id}", response_model=schemas.Registration, status_code=status.HTTP_200_OK)
def read_registration(registration_id: int, db: Session = Depends(get_db)):
    db_registration = crud.get_registration(db, registration_id=registration_id)
    if db_registration is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration not found")
    return db_registration


@app.get("/registrations/", response_model=List[schemas.Registration])
def read_registrations(db: Session = Depends(get_db)):
    db_registrations = crud.get_all_registrations(db)
    return db_registrations



@app.put("/registrations/{registration_id}", response_model=schemas.Registration, status_code=status.HTTP_200_OK)
def update_registration(registration_id: int, registration: schemas.RegistrationUpdate, db: Session = Depends(get_db)):
    db_registration = crud.update_registration(db, registration_id, registration)
    if db_registration is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration not found")
    return db_registration



@app.delete("/registrations/{registration_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_registration(registration_id: int, db: Session = Depends(get_db)):
    success = crud.delete_registration(db, registration_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration not found")
    return {"detail": "Registration deleted successfully"}


# Students Endpoints

@app.post("/students/", response_model=schemas.Student)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    return crud.create_student(db=db, student=student)



@app.get("/students/{student_id}", response_model=schemas.Student)
def read_student(student_id: int, db: Session = Depends(get_db)):
    db_student = db.query(Student).filter(Student.student_id == student_id).first()
    if db_student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return db_student



@app.patch("/students/{student_id}", response_model=schemas.Student)
def update_student(student_id: int, student: schemas.Student, db: Session = Depends(get_db)):
    try:
        updated_student = crud.update_student(db, student_id, student)
        if updated_student is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        return updated_student
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    success = crud.delete_student(db, student_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return {"detail": "Student deleted successfully"}



@app.get("/students/", response_model=list[schemas.Student])
def read_students(
    page_size: int = Query(10, alias="PageSize", gt=0),
    page_number: int = Query(1, alias="PageNumber", gt=0),
    sort_by: SortBy = Query(SortBy.nombre, alias="SortParameter.SortBy"),
    sort_direction: SortDirection = Query(SortDirection.desc, alias="SortParameter.SortDirection"),
    db: Session = Depends(get_db)):

    students_query = db.query(models.Student)

    # Sorting logic

    if sort_direction == "asc":
        students_query = students_query.order_by(getattr(models.Student, sort_by.value).asc())
    else:
        students_query = students_query.order_by(getattr(models.Student, sort_by.value).desc())

    # Pagination logic
    offset = (page_number - 1) * page_size
    students_query = students_query.offset(offset).limit(page_size)

    # Execute query and fetch data
    students = students_query.all()

    return students


@app.get("/students/{student_id}/subjects/", response_model=List[schemas.Subject])
def get_student_subjects(student_id: int, db: Session = Depends(get_db)):
    subjects = db.query(models.Subject).\
        join(models.Registration, models.Subject.subject_id == models.Registration.subject_id).\
        filter(models.Registration.student_id == student_id).all()
    return subjects


# Subject Endpoints


@app.post("/subjects/", response_model=schemas.Subject, status_code=status.HTTP_201_CREATED)
def create_subject(subject: schemas.SubjectCreate, db: Session = Depends(get_db)):
    return crud.create_subject(db=db, subject=subject)



@app.get("/subjects/{subject_id}", response_model=schemas.Subject, status_code=status.HTTP_200_OK)
def read_subject(subject_id: int, db: Session = Depends(get_db)):
    db_subject = crud.get_subject(db, subject_id=subject_id)
    if db_subject is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
    return db_subject


@app.get("/subjects/", response_model=list[schemas.Subject])
def read_subject(
    page_size: int = Query(10, alias="PageSize", gt=0),
    page_number: int = Query(1, alias="PageNumber", gt=0),
    sort_by: SortBySubject = Query(SortBySubject.nombre, alias="SortParameter.SortBy"),
    sort_direction: SortDirection = Query(SortDirection.desc, alias="SortParameter.SortDirection"),
    db: Session = Depends(get_db)):

    subjects_query = db.query(models.Subject)

    if sort_direction == "asc":
        subjects_query = subjects_query.order_by(getattr(models.Subject, sort_by.value).asc())
    else:
        subjects_query = subjects_query.order_by(getattr(models.Subject, sort_by.value).desc())

    # Pagination logic
    offset = (page_number - 1) * page_size
    subjects_query = subjects_query.offset(offset).limit(page_size)

    # Execute query and fetch data
    subjects = subjects_query.all()

    return subjects


@app.put("/subjects/{subject_id}", response_model=schemas.Subject, status_code=status.HTTP_200_OK)
def update_subject(subject_id: int, subject: schemas.SubjectUpdate, db: Session = Depends(get_db)):
    db_subject = crud.update_subject(db, subject_id, subject)
    if db_subject is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
    return db_subject



@app.delete("/subjects/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    success = crud.delete_subject(db, subject_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
    return {"detail": "Subject deleted successfully"}


@app.get("/subjects/{subject_id}/students/", response_model=List[schemas.Student])
def get_subject_students(subject_id: int, db: Session = Depends(get_db)):
    students = db.query(models.Student).\
        join(models.Registration, models.Student.student_id == models.Registration.student_id).\
        filter(models.Registration.subject_id == subject_id).all()
    return students




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8109)

