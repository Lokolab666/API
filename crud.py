from sqlalchemy.orm import Session
import models, schemas
<<<<<<< HEAD
from models import Estudiante, Subject, Inscripcion

# CRUD for Estudiante
def create_student(db: Session, student: schemas.StudentCreate):
    db_student = models.Estudiante(
        estudiante_name=student.estudiante_name,
        estudiante_last_name=student.estudiante_last_name,
        estudiante_code=student.estudiante_code,
        estudiante_type_doc=student.estudiante_type_doc,
        estudiante_document=student.estudiante_document,
        estudiante_status=student.estudiante_status,
        estudiante_photo=student.estudiante_photo,
        estudiante_programa_fk=student.estudiante_programa_fk
=======
from models import Student, Subject, Registration

# CRUD for student
def create_student(db: Session, student: schemas.StudentCreate):
    db_student = models.Student(
        nombre=student.nombre,
        codigo=student.codigo,
        numero_identificacion=student.numero_identificacion
>>>>>>> 667e0fedd15dc0637307a7611f2e93b428a3b118
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def get_student(db: Session, student_id: int):
<<<<<<< HEAD
    return db.query(Estudiante).filter(Estudiante.estudiante_id == student_id).first()


def update_student(db: Session, student_id: int, student: schemas.StudentUpdate):
    db_student = db.query(models.Estudiante).filter(Estudiante.estudiante_id == student_id).first()
    if not db_student:
        return None
    
    if student.estudiante_name is not None:
        db_student.estudiante_name = student.estudiante_name
    if student.estudiante_last_name is not None:
        db_student.estudiante_last_name = student.estudiante_last_name
    if student.estudiante_code is not None:
        db_student.estudiante_code = student.estudiante_code
    if student.estudiante_type_doc is not None:
        db_student.estudiante_type_doc = student.estudiante_type_doc
    if student.estudiante_document is not None:
        db_student.estudiante_document = student.estudiante_document
    if student.estudiante_status is not None:
        db_student.estudiante_status = student.estudiante_status
    if student.estudiante_photo is not None:
        db_student.estudiante_photo = student.estudiante_photo
=======
    return db.query(Student).filter(Student.student_id == student_id).first()


def update_student(db: Session, student_id: int, student: schemas.StudentUpdate):
    db_student = db.query(models.Student).filter(Student.student_id == student_id).first()
    if not db_student:
        return None
    
    if student.nombre is not None:
        db_student.nombre = student.nombre
    if student.codigo is not None:
        db_student.codigo = student.codigo
    if student.numero_identificacion is not None:
        db_student.numero_identificacion = student.numero_identificacion
>>>>>>> 667e0fedd15dc0637307a7611f2e93b428a3b118

    db.commit()
    db.refresh(db_student)

    return db_student


def delete_student(db: Session, student_id: int):
<<<<<<< HEAD
    db_student = db.query(models.Estudiante).filter(Estudiante.estudiante_id == student_id).first()
=======
    db_student = db.query(models.Student).filter(Student.student_id == student_id).first()
>>>>>>> 667e0fedd15dc0637307a7611f2e93b428a3b118
    if db_student:
        db.delete(db_student)
        db.commit()
        return True
    return False

# CRUD for Subject
def create_subject(db: Session, subject: schemas.SubjectCreate):
    db_subject = models.Subject(
        nombre=subject.nombre,
        aula=subject.aula,
        creditos=subject.creditos,
<<<<<<< HEAD
        cupos=subject.cupos,
        programa_fk=subject.programa_fk
=======
        cupos=subject.cupos
>>>>>>> 667e0fedd15dc0637307a7611f2e93b428a3b118
    )
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
<<<<<<< HEAD
        db_subject.aula = subject.aula
        db_subject.creditos = subject.creditos
        db_subject.cupos = subject.cupos
=======
>>>>>>> 667e0fedd15dc0637307a7611f2e93b428a3b118
        db.commit()
        db.refresh(db_subject)
    return db_subject


<<<<<<< HEAD
def delete_subject(db: Session, subject_id: int):
=======
def delete_course(db: Session, subject_id: int):
>>>>>>> 667e0fedd15dc0637307a7611f2e93b428a3b118
    db_subject = db.query(models.Subject).filter(Subject.subject_id == subject_id).first()
    if db_subject:
        db.delete(db_subject)
        db.commit()
        return True
    return False


<<<<<<< HEAD
# CRUD for Inscripcion
def create_registration(db: Session, registration: schemas.RegistrationCreate):
    db_registration = models.Inscripcion(
        student_id=registration.student_id,
        grupo_id=registration.grupo_id
    )
=======
#CRUD for Registration
def create_registration(db: Session, registration: schemas.RegistrationCreate):
    db_registration = models.Registration(**registration.dict())
>>>>>>> 667e0fedd15dc0637307a7611f2e93b428a3b118
    db.add(db_registration)
    db.commit()
    db.refresh(db_registration)
    return db_registration


def get_registration(db: Session, registration_id: int):
<<<<<<< HEAD
    return db.query(Inscripcion).filter(Inscripcion.inscripcion_id == registration_id).first()


def update_registration(db: Session, registration_id: int, registration: schemas.RegistrationUpdate):
    db_registration = db.query(Inscripcion).filter(Inscripcion.inscripcion_id == registration_id).first()
=======
    return db.query(Registration).filter(Registration.inscripcion_id == registration_id).first()


def update_registration(db: Session, registration_id: int, registration: schemas.RegistrationUpdate):
    db_registration = db.query(Registration).filter(Registration.inscripcion_id == registration_id).first()
>>>>>>> 667e0fedd15dc0637307a7611f2e93b428a3b118
    if db_registration:
        db_registration.subject_id = registration.subject_id
        db_registration.student_id = registration.student_id
        db.commit()
        db.refresh(db_registration)
    return db_registration


def delete_registration(db: Session, registration_id: int):
<<<<<<< HEAD
    db_registration = db.query(Inscripcion).filter(Inscripcion.inscripcion_id == registration_id).first()
=======
    db_registration = db.query(Registration).filter(Registration.inscripcion_id == registration_id).first()
>>>>>>> 667e0fedd15dc0637307a7611f2e93b428a3b118
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


def get_all_registrations(db: Session):
<<<<<<< HEAD
    return db.query(models.Inscripcion).all()
=======
    return db.query(models.Registration).all()
>>>>>>> 667e0fedd15dc0637307a7611f2e93b428a3b118
