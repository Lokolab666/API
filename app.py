from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, crud
from database import SessionLocal, engine
import uvicorn

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.post("/registrations/", response_model=schemas.Inscription)
def create_registration(registration: schemas.InscriptionCreate, db: Session = Depends(get_db)):
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


@app.post("/students/", response_model=schemas.Student)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    return crud.create_student(db=db, student=student)


@app.get("/students/{student_id}", response_model=StudentSchema)
def read_student(student_id: int, db: Session = Depends(get_db)):
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if db_student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return db_student


@app.patch("/students/{student_id}", response_model=StudentSchema)
def update_student(student_id: int, student: StudentSchema, db: Session = Depends(get_db)):
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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8109)

