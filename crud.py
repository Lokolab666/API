from sqlalchemy.orm import Session
import models, schemas
from models import Student, Subject, Registration

# CRUD for student
def create_student(db: Session, student: schemas.StudentCreate):
    db_student = models.Student(name=student.nombre)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def get_student(db: Session, student_id: int):
    return db.query(Student).filter(Student.student_id == student_id).first()


def update_student(db: Session, student_id: int, student: schemas.StudentUpdate):
    db_student = db.query(models.Student).filter(Student.student_id == student_id).first()
    if db_student:
        db_student.nombre = student.nombre
        db.commit()
        db.refresh(db_student)
    return db_student


def delete_student(db: Session, student_id: int):
    db_student = db.query(models.Student).filter(Student.student_id == student_id).first()
    if db_student:
        db.delete(db_student)
        db.commit()
        return True
    return False

# CRUD for Subject
def create_subject(db: Session, subject: schemas.SubjectCreate):
    db_subject = models.Subject(materia_id=subject.materia_id)
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject


def get_subject(db: Session, subject_id: int):
    return db.query(Subject).filter(Subject.subject_id == subject_id).first()


def update_subject(db: Session, subject_id: int, subject: schemas.SubjectUpdate):
    db_subject = db.query(models.Subject).filter(Subject.subject_id == subject_id).first()
    if db_subject:
        db_subject.nombre = subject.nombre
        db.commit()
        db.refresh(db_subject)
    return db_subject


def delete_course(db: Session, subject_id: int):
    db_subject = db.query(models.Subject).filter(Subject.subject_id == subject_id).first()
    if db_subject:
        db.delete(db_subject)
        db.commit()
        return True
    return False


#CRUD for Registration
def create_registration(db: Session, registration: schemas.RegistrationCreate):
    db_registration = models.Registration(**registration.dict())
    db.add(db_registration)
    db.commit()
    db.refresh(db_registration)
    return db_registration


def get_registration(db: Session, registration_id: int):
    return db.query(Registration).filter(Registration.inscripcion_id == registration_id).first()


def update_registration(db: Session, registration_id: int, registration: schemas.RegistrationUpdate):
    db_registration = db.query(Registration).filter(Registration.inscripcion_id == registration_id).first()
    if db_registration:
        db_registration.inscripcion_id = registration.materia_id
        db_registration.student_id = registration.estudiante_id
        db.commit()
        db.refresh(db_registration)
    return db_registration


def delete_registration(db: Session, registration_id: int):
    db_registration = db.query(Registration).filter(Registration.inscripcion_id == registration_id).first()
    if db_registration:
        db.delete(db_registration)
        db.commit()
        return True
    return False


def update_subject_counter(db: Session, subject_id: int):
    subject = db.query(models.Subject).filter(models.Subject.subject_id == subject_id).first()
    if subject:
        subject.cont += 1
        db.commit()
        db.refresh(subject)
        if subject.cont <= subject.cupos:
            new_instance = subject.create_new_instance(db)
            return new_instance
        return subject
    return None
