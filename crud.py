from sqlalchemy.orm import Session
import models, schemas
from models import Estudiante, Inscripcion, Facultad, Programa, Asignatura, Grupo
import bcrypt
from fastapi import FastAPI, Depends, HTTPException, status, Query, Request, UploadFile, File
from google.cloud import storage

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
        estudiante_programa_fk=student.estudiante_programa_fk,
        estudiante_autenticacion_fk=student.estudiante_autenticacion_fk
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def get_student(db: Session, student_id: int):
    return db.query(Estudiante).filter(Estudiante.estudiante_id == student_id).first()

def upload_file_to_gcs(file: UploadFile, bucket_name: str, blob_name: str) -> str:
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(file.file.read(), content_type=file.content_type)
    file.file.close()
    return blob.public_url


def update_student(db: Session, student_id: int, student: schemas.StudentUpdate, photo: UploadFile = File(None)):
    db_student = db.query(models.Estudiante).filter(Estudiante.estudiante_id == student_id).first()
    if not db_student:
        return None
    
    if student.estudiante_name is not None:
        db_student.estudiante_name = student.estudiante_name
    if student.estudiante_last_name is not None:
        db_student.estudiante_last_name = student.estudiante_last_name
    if student.estudiante_type_doc is not None:
        db_student.estudiante_type_doc = student.estudiante_type_doc
    if student.estudiante_status is not None:
        db_student.estudiante_status = student.estudiante_status
    
    if photo:
        if not photo.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File provided is not an image.")
        photo_url = upload_file_to_gcs(photo, 'fotos_sira', f'photos/{student_id}')
        db_student.estudiante_photo = photo_url

    db.commit()
    db.refresh(db_student)

    return db_student


def delete_student(db: Session, student_id: int):
    db_student = db.query(models.Estudiante).filter(Estudiante.estudiante_id == student_id).first()
    if db_student:
        db.delete(db_student)
        db.commit()
        return True
    return False

# CRUD for Subject

def create_subject(db: Session, asignatura: schemas.SubjectCreate):
    db_subject = models.Asignatura(
        asignatura_nombre=asignatura.asignatura_nombre,
        programa_fk=asignatura.programa_fk
    )
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject


def get_subject(db: Session, subject_id: int):
    return db.query(Asignatura).filter(Asignatura.asignatura_id == subject_id).first()


def get_all_subjects(db: Session):
    return db.query(Asignatura).all()


def update_subject(db: Session, subject_id: int, asignatura: schemas.SubjectUpdate):
    db_subject = db.query(models.Asignatura).filter(Asignatura.asignatura_id == subject_id).first()
    if db_subject:
        db_subject.asignatura_nombre = asignatura.asignatura_nombre
        db.commit()
        db.refresh(db_subject)
    return db_subject


def delete_subject(db: Session, subject_id: int):
    db_subject = db.query(models.Asignatura).filter(Asignatura.asignatura_id == subject_id).first()
    if db_subject:
        db.delete(db_subject)
        db.commit()
        return True
    return False


# CRUD for Inscripcion

def manage_subject_groups(db: Session, subject_name: str, max_groups=3):
    # Fetch all groups for this subject base name
    base_subject_name = subject_name.split(" - Group")[0].strip()
    subject_groups = db.query(Grupo).filter(Grupo.grupo_name.like(f"{base_subject_name}%")).all()

    available_groups = [group for group in subject_groups if db.query(Inscripcion).filter_by(grupo_fk=group.grupo_id).count() < group.grupo_quotas]
    
    if available_groups:
        return available_groups[0]

    # If all groups are full and less than max_groups, create a new group
    if len(subject_groups) < max_groups:
        last_group_number = max([int(g.grupo_name.split("Group ")[-1]) for g in subject_groups]) if subject_groups else 0
        new_group_number = last_group_number + 1
        new_group_name = f"{base_subject_name} - Group {new_group_number}"
        new_group = Grupo(
            grupo_name=new_group_name,
            grupo_classroom=subject_groups[0].grupo_classroom,
            grupo_credits=subject_groups[0].grupo_credits,
            grupo_quotas=subject_groups[0].grupo_quotas,
            cont=0,
            asignatura_fk=subject_groups[0].asignatura_fk
        )
        db.add(new_group)
        db.commit()
        return new_group

    return None  # If no groups are available and max_groups is reached, return None

def get_subject_by_name(db: Session, asignatura_nombre: str):
    return db.query(models.Asignatura).filter(models.Asignatura.asignatura_nombre == asignatura_nombre).first()



def create_registration(db: Session, estudiante_fk: int, subject_name: str):
    subject_group = manage_subject_groups(db, subject_name)

    if subject_group is None:
        raise Exception("No available groups for this subject or maximum group limit reached.")

    # Check if the student is already registered in any group of this subject
    existing_registration = db.query(Inscripcion).join(Grupo).filter(
        Inscripcion.estudiante_fk == estudiante_fk,
        Grupo.grupo_name.like(f"{subject_name.split(' - Group')[0].strip()}%")
    ).first()

    if existing_registration:
        raise Exception("Student is already registered in a group of this subject.")

    # Create the new registration
    new_registration = Inscripcion(estudiante_fk=estudiante_fk, grupo_fk=subject_group.grupo_id)
    
    db.add(new_registration)
    db.commit()
    return new_registration

def process_registration(db: Session, estudiante_id: int, grupo_id: int):
    # Retrieve student and group information
    db_student = get_student(db, estudiante_id)
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    db_group = db.query(Grupo).filter(Grupo.grupo_id == grupo_id).first()
    if db_group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Handle subject group management and registration creation
    subject_name = db_group.grupo_name
    subject_group = manage_subject_groups(db, subject_name)
    if subject_group is None:
        raise HTTPException(status_code=400, detail="No available groups for this subject or maximum group limit reached.")

    # Check if the student is already registered in any group of this subject
    existing_registration = db.query(Inscripcion).join(Grupo).filter(
        Inscripcion.estudiante_fk == estudiante_id,
        Grupo.grupo_name.like(f"{subject_name.split(' - Group')[0].strip()}%")
    ).first()

    if existing_registration:
        raise HTTPException(status_code=400, detail="Student is already registered in a group of this subject.")

    # Create the new registration
    new_registration = Inscripcion(estudiante_fk=estudiante_id, grupo_fk=subject_group.grupo_id)
    db.add(new_registration)
    db.commit()
    return new_registration


def get_registration(db: Session, registration_id: int):
    return db.query(Inscripcion).filter(Inscripcion.inscripcion_id == registration_id).first()


def get_all_registrations(db: Session):
    return db.query(Inscripcion).all()


def update_registration(db: Session, registration_id: int, registration: schemas.InscriptionUpdate):
    db_registration = db.query(Inscripcion).filter(Inscripcion.inscripcion_id == registration_id).first()
    if db_registration:
        db_registration.grupo_fk = registration.subject_id
        db_registration.estudiante_fk = registration.student_id
        db.commit()
        db.refresh(db_registration)
    return db_registration


def delete_registration(db: Session, registration_id: int):
    db_registration = db.query(Inscripcion).filter(Inscripcion.inscripcion_id == registration_id).first()
    if db_registration:
        db.delete(db_registration)
        db.commit()
        return True
    return False


""" def update_subject_counter(db: Session, subject_id: int):
    subject = db.query(Asignatura).filter(models.Asignatura.asignatura_id == subject_id).first()
    if subject:
        subject.cont += 1
        db.commit()
        db.refresh(subject)
        if subject.cont <= subject.cupos:
            new_instance = subject.create_new_instance(db)
            return new_instance
        return subject
    return None """


# CRUD for Facultad

def create_facultad(db: Session, facultad: schemas.FacultadCreate):
    db_facultad = models.Facultad(
        facultad_name=facultad.facultad_name
    )
    db.add(db_facultad)
    db.commit()
    db.refresh(db_facultad)
    return db_facultad


def get_facultad(db: Session, facultad_id: int):
    return db.query(models.Facultad).filter(models.Facultad.facultad_id == facultad_id).first()


def get_all_facultad(db: Session):
    return db.query(Facultad).all()


def update_facultad(db: Session, facultad_id: int, facultad: schemas.FacultadUpdate):
    db_facultad = db.query(models.Facultad).filter(models.Facultad.facultad_id == facultad_id).first()
    if db_facultad:
        db_facultad.facultad_name = facultad.facultad_name
        db.commit()
        db.refresh(db_facultad)
    return db_facultad


def delete_facultad(db: Session, facultad_id: int):
    db_facultad = db.query(models.Facultad).filter(models.Facultad.facultad_id == facultad_id).first()
    if db_facultad:
        db.delete(db_facultad)
        db.commit()
        return True
    return False


# CRUD Programa

def create_programa(db: Session, programa: schemas.ProgramaCreate):
    db_programa = models.Programa(
        programa_name=programa.programa_name,
        facultad_fk=programa.facultad_fk
    )
    db.add(db_programa)
    db.commit()
    db.refresh(db_programa)
    return db_programa


def get_programa(db: Session, programa_id: int):
    return db.query(models.Programa).filter(models.Programa.programa_id == programa_id).first()


def get_all_programa(db: Session):
    return db.query(Programa).all()


def update_programa(db: Session, programa_id: int, programa: schemas.ProgramaUpdate):
    db_programa = db.query(models.Programa).filter(models.Programa.programa_id == programa_id).first()
    if db_programa:
        db_programa.programa_name = programa.programa_name
        db_programa.facultad_fk = programa.facultad_fk
        db.commit()
        db.refresh(db_programa)
    return db_programa


def delete_programa(db: Session, programa_id: int):
    db_programa = db.query(models.Programa).filter(models.Programa.programa_id == programa_id).first()
    if db_programa:
        db.delete(db_programa)
        db.commit()
        return True
    return False

# CRUD for Autenticacion

def create_autenticacion(db: Session, autenticacion: schemas.AutenticacionCreate):
    hashed_password = bcrypt.hashpw(autenticacion.autenticacion_password.encode('utf-8'), bcrypt.gensalt())
    db_autenticacion = models.Autenticacion(
        autenticacion_user=autenticacion.autenticacion_user,
        autenticacion_password=hashed_password.decode('utf-8'),
        rol_fk=autenticacion.rol_fk
    )
    db.add(db_autenticacion)
    db.commit()
    db.refresh(db_autenticacion)
    return db_autenticacion
    


def get_autenticacion(db: Session, aut_id: int):
    return db.query(models.Autenticacion).filter(models.Autenticacion.aut_id == aut_id).first()


def get_all_autenticacion(db: Session):
    return db.query(models.Autenticacion).all()


def update_autenticacion(db: Session, aut_id: int, autenticacion: schemas.AutenticacionUpdate):
    db_autenticacion = db.query(models.Autenticacion).filter(models.Autenticacion.aut_id == aut_id).first()
    hashed_password = bcrypt.hashpw(autenticacion.autenticacion_password.encode('utf-8'), bcrypt.gensalt())
    if db_autenticacion:
        db_autenticacion.autenticacion_user = autenticacion.autenticacion_user
        db_autenticacion.autenticacion_password = hashed_password.decode('utf-8'),
        db_autenticacion.rol_fk = autenticacion.rol_fk
        db.commit()
        db.refresh(db_autenticacion)
    return db_autenticacion


def delete_autenticacion(db: Session, aut_id: int):
    db_autenticacion = db.query(models.Autenticacion).filter(models.Autenticacion.aut_id == aut_id).first()
    if db_autenticacion:
        db.delete(db_autenticacion)
        db.commit()
        return True
    return False

# CRUD for Grupo

def create_grupo(db: Session, grupo: schemas.GroupCreate):
    db_grupo = models.Grupo(
        grupo_name=grupo.grupo_name,
        grupo_classroom=grupo.grupo_classroom,
        grupo_credits=grupo.grupo_credits,
        grupo_quotas=grupo.grupo_quotas,
        asignatura_fk=grupo.asignatura_fk
    )
    db.add(db_grupo)
    db.commit()
    db.refresh(db_grupo)
    return db_grupo


def get_grupo(db: Session, grupo_id: int):
    return db.query(models.Grupo).filter(models.Grupo.grupo_id == grupo_id).first()


def get_all_grupo(db: Session):
    return db.query(models.Grupo).all()


def update_grupo(db: Session, grupo_id: int, grupo: schemas.GroupUpdate):
    db_grupo = db.query(models.Grupo).filter(models.Grupo.grupo_id == grupo_id).first()
    if db_grupo:
        db_grupo.grupo_name = grupo.grupo_name
        db_grupo.grupo_classroom = grupo.grupo_classroom
        db_grupo.grupo_credits = grupo.grupo_credits
        db_grupo.grupo_quotas = grupo.grupo_quotas
        db.commit()
        db.refresh(db_grupo)
    return db_grupo


def delete_grupo(db: Session, grupo_id: int):
    db_grupo = db.query(models.Grupo).filter(models.Grupo.grupo_id == grupo_id).first()
    if db_grupo:
        db.delete(db_grupo)
        db.commit()
        return True
    return False

# CRUD for Rol

def create_rol(db: Session, rol: schemas.RolCreate):
    db_rol = models.Rol(
        nombre=rol.nombre
    )
    db.add(db_rol)
    db.commit()
    db.refresh(db_rol)
    return db_rol


def get_rol(db: Session, rol_id: int):
    return db.query(models.Rol).filter(models.Rol.rol_id == rol_id).first()


def get_all_rol(db: Session):
    return db.query(models.Rol).all()


def update_rol(db: Session, rol_id: int, rol: schemas.RolUpdate):
    db_rol = db.query(models.Rol).filter(models.Rol.rol_id == rol_id).first()
    if db_rol:
        db_rol.nombre = rol.nombre
        db.commit()
        db.refresh(db_rol)
    return db_rol


def delete_rol(db: Session, rol_id: int):
    db_rol = db.query(models.Rol).filter(models.Rol.rol_id == rol_id).first()
    if db_rol:
        db.delete(db_rol)
        db.commit()
        return True
    return False



