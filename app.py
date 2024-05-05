from fastapi import FastAPI, Depends, HTTPException, status, Query
from typing import Optional
from sqlalchemy.orm import Session
import models, schemas, crud
from database import SessionLocal, engine
from models import Student, Subject, Registration
import uvicorn

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#Registration Endpoints

@app.post("/registrations/", response_model=schemas.Registration)
def create_registration(registration: schemas.RegistrationCreate, db: Session = Depends(get_db)):
    db_student = crud.get_student(db, registration.student_id)
    db_subject = crud.get_subject(db, registration.subject_id)
    if db_student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    if db_subject is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
    if db_subject.cont >= db_subject.cupos:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Subject already full")
    existing_registration = db.query(Registration).filter(  
        Registration.student_id == registration.student_id,
        Registration.subject_id == registration.subject_id
    ).first()
    
    if existing_registration:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student already registered for this subject")
    
    new_registration = crud.create_registration(db=db, registration=registration)
    crud.update_subject_counter(db, registration.subject_id)
    raise HTTPException(status_code=status.HTTP_200_OK, detail="Student OK to register")
    
    # return new_registration

@app.get("/registrations/{registration_id}", response_model=schemas.Registration, status_code=status.HTTP_200_OK)
def read_registration(registration_id: int, db: Session = Depends(get_db)):
    db_registration = crud.get_registration(db, registration_id=registration_id)
    if db_registration is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration not found")
    return db_registration


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
    sort_by: Optional[str] = Query("created_at", alias="SortBy", regex="^(nombre|apellido|numero_identificacion|created_at)$"),
    sort_direction: str = Query("desc", alias="SortDirection", regex="^(asc|desc)$"),
    db: Session = Depends(get_db)):

    students_query = db.query(models.Student)

    # Sorting logic
    if sort_by == "nombre":
        students_query = students_query.order_by(models.Student.nombre.desc() if sort_direction == "desc" else models.Student.nombre.asc())
    elif sort_by == "apellido":
        students_query = students_query.order_by(models.Student.apellido.desc() if sort_direction == "desc" else models.Student.apellido.asc())
    elif sort_by == "numero_identificacion":
        students_query = students_query.order_by(models.Student.numero_identificacion.desc() if sort_direction == "desc" else models.Student.numero_identificacion.asc())
    else:
        # Default sort by created_at
        students_query = students_query.order_by(models.Student.created_at.desc() if sort_direction == "desc" else models.Student.created_at.asc())

    # Pagination logic
    offset = (page_number - 1) * page_size
    students_query = students_query.offset(offset).limit(page_size)

    # Execute query and fetch data
    students = students_query.all()

    return students

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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8109)

