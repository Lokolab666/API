from fastapi import FastAPI, Depends, HTTPException, status, Query, Request, UploadFile, File, Form
from typing import List, Optional
from sqlalchemy.orm import Session
import models, schemas, crud
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
from models import Estudiante, Inscripcion
import uvicorn
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from enum import Enum
import os
from google.cloud import storage
from PIL import Image
from io import BytesIO
import asyncio
import bcrypt
from sqlalchemy.orm import joinedload
import face_recognition
import io


models.Base.metadata.create_all(bind=engine)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "deft-justice-424603-k3-bbeade0785bd.json"
client = storage.Client()


class SortBy(str, Enum):
    estudiante_id = "estudiante_id"
    estudiante_name = "estudiante_name"
    estudiante_last_name = "estudiante_last_name"
    estudiante_code = "estudiante_code"
    estudiante_document = "estudiante_document"

class SortByGrupo(str, Enum):
    grupo_id = "grupo_id"
    grupo_name = "grupo_name"
    grupo_classroom = "grupo_classroom"
    grupo_credits = "grupo_credits"
    grupo_quotas = "grupo_quotas"


class SortDirection(str, Enum):
    asc = "asc"
    desc = "desc"


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    elif exc.status_code == 400:
        return JSONResponse(
            status_code=400,
            content={"message": "Incorrect data"},
        )
    # Pass other status codes to the default handler
    return await request.app.default_exception_handler(request, exc)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

#Registration Endpoints

@app.post("/crear_inscripcion/", response_model=schemas.Inscription)
def create_registration(inscripcion: schemas.InscriptionCreate, db: Session = Depends(get_db)):
    return crud.process_registration(db=db, estudiante_id=inscripcion.estudiante_fk, grupo_id=inscripcion.grupo_fk)



@app.get("/ver_inscripcion/{registration_id}", response_model=schemas.Inscription, status_code=status.HTTP_200_OK)
def read_registration(registration_id: int, db: Session = Depends(get_db)):
    db_registration = crud.get_registration(db, registration_id=registration_id)
    if db_registration is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration not found")
    return db_registration

# TODO: check if this is the correct way to return a list of registrations
@app.get("/inscripciones/", response_model=List[schemas.Inscription])
def read_registrations(db: Session = Depends(get_db)):
    db_registrations = crud.get_all_registrations(db)
    return db_registrations



@app.put("/actualizar_inscripcion/{registration_id}", response_model=schemas.Inscription, status_code=status.HTTP_200_OK)
def update_registration(registration_id: int, registration: schemas.InscriptionUpdate, db: Session = Depends(get_db)):
    db_registration = crud.update_registration(db, registration_id, registration)
    if db_registration is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration not found")
    return db_registration



@app.delete("/borrar_inscripcion/{registration_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_registration(registration_id: int, db: Session = Depends(get_db)):
    success = crud.delete_registration(db, registration_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration not found")
    return {"detail": "Registration deleted successfully"}


# Students Endpoints

def upload_file_to_gcs(file: UploadFile, bucket_name: str, blob_name: str) -> str:
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    image = Image.open(file.file)

    if image.format != 'JPEG':
        byte_array = BytesIO()
        image.save(byte_array, format='JPEG')
        image_bytes = byte_array.getvalue()
    else:
        # Otherwise, just read the resized image into bytes
        byte_array = BytesIO()
        image.save(byte_array, format=image.format)
        image_bytes = byte_array.getvalue()
    
    blob.upload_from_string(image_bytes, content_type='image/jpeg')
    file.file.close()  # Always close the file handler
    
    return blob.public_url


@app.post("/crear_estudiante/", response_model=schemas.Student)
async def create_student(
    estudiante_name: str = Form(...),
    estudiante_last_name: str = Form(...),
    estudiante_code: str = Form(...),
    estudiante_type_doc: str = Form(...),
    estudiante_document: str = Form(...),
    estudiante_status: str = Form(...),
    estudiante_programa_fk: int = Form(...),
    estudiante_autenticacion_fk: int = Form(...),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    
    student_data = schemas.StudentCreate(
        estudiante_name=estudiante_name,
        estudiante_last_name=estudiante_last_name,
        estudiante_code=estudiante_code,
        estudiante_type_doc=estudiante_type_doc,
        estudiante_document=estudiante_document,
        estudiante_status=estudiante_status,
        estudiante_programa_fk=estudiante_programa_fk,
        estudiante_autenticacion_fk=estudiante_autenticacion_fk
    )

    new_student = crud.create_student(db=db, student=student_data)
    db.commit()

    if photo.content_type != 'image/jpeg':
        raise HTTPException(status_code=400, detail="Only JPEG images are accepted.")
    
    photo_url = upload_file_to_gcs(photo, 'fotos_sira', f'photos/{new_student.estudiante_id}')

    new_student.estudiante_photo = photo_url
    db.commit()

    db.refresh(new_student)
    
    return new_student


@app.get("/estudiantes/{student_id}", response_model=schemas.Student)
def read_student(student_id: int, db: Session = Depends(get_db)):
    db_student = crud.get_student(db, student_id=student_id)
    if db_student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return db_student



@app.patch("/actualizar_estudiante/{student_id}", response_model=schemas.Student)
async def update_student(
    student_id: int,
    estudiante_name: Optional[str] = Form(None),
    estudiante_last_name: Optional[str] = Form(None),
    estudiante_type_doc: Optional[str] = Form(None),
    estudiante_status: Optional[str] = Form(None),
    photo: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    student_data = schemas.StudentUpdate(
        estudiante_name=estudiante_name,
        estudiante_last_name=estudiante_last_name,
        estudiante_type_doc=estudiante_type_doc,
        estudiante_status=estudiante_status
    )
    
    # Process the update operation
    updated_student = crud.update_student(db, student_id, student_data, photo)
    if not updated_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return updated_student



@app.delete("/eliminar_estudiante/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    success = crud.delete_student(db, student_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return {"detail": "Student deleted successfully"}



@app.get("/estudiantes/", response_model=list[schemas.Student])
def read_students(
    page_size: int = Query(10, alias="PageSize", gt=0),
    page_number: int = Query(1, alias="PageNumber", gt=0),
    sort_by: SortBy = Query(SortBy.estudiante_code, alias="SortParameter.SortBy"),
    sort_direction: SortDirection = Query(SortDirection.desc, alias="SortParameter.SortDirection"),
    db: Session = Depends(get_db)):

    students_query = db.query(models.Estudiante)

    if sort_direction == "asc":
        students_query = students_query.order_by(getattr(models.Estudiante, sort_by.value).asc())
    else:
        students_query = students_query.order_by(getattr(models.Estudiante, sort_by.value).desc())

    offset = (page_number - 1) * page_size
    students_query = students_query.offset(offset).limit(page_size)

    students = students_query.all()

    return students



@app.get("/estudiantes/{student_id}/materias_grupo/", response_model=List[schemas.Group])
def get_student_subjects(student_id: int, db: Session = Depends(get_db)):
    groups = db.query(models.Grupo).\
        options(joinedload(models.Grupo.asignatura)).\
        join(models.Inscripcion, models.Grupo.grupo_id == models.Inscripcion.grupo_fk).\
        filter(models.Inscripcion.estudiante_fk == student_id).all()
    if not groups:
        raise HTTPException(status_code=404, detail="No groups found for this student")
    return groups


# Subject Endpoints


@app.post("/crear_asignatura/", response_model=schemas.Subject, status_code=status.HTTP_201_CREATED)
def create_subject(asignatura: schemas.SubjectCreate, db: Session = Depends(get_db)):
    return crud.create_subject(db=db, asignatura=asignatura)


@app.get("/asignatura/{subject_id}", response_model=schemas.Subject, status_code=status.HTTP_200_OK)
def read_subject(subject_id: int, db: Session = Depends(get_db)):
    db_subject = crud.get_subject(db, subject_id=subject_id)
    if db_subject is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
    return db_subject


@app.get("/asignaturas/", response_model=list[schemas.Subject])
def read_asignaturas(db: Session = Depends(get_db)):
    subjects = crud.get_all_subjects(db)
    return subjects



@app.put("/actualizar_asignatura/{subject_id}", response_model=schemas.Subject, status_code=status.HTTP_200_OK)
def update_subject(subject_id: int, subject: schemas.SubjectUpdate, db: Session = Depends(get_db)):
    db_subject = crud.update_subject(db, subject_id, subject)
    if db_subject is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
    return db_subject



@app.delete("/borrar_asignatura/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    success = crud.delete_subject(db, subject_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
    return {"detail": "Subject deleted successfully"}


@app.get("/grupo_asignaturas/{grupo_id}/estudiantes/", response_model=List[schemas.Student])
def get_subject_students(grupo_id: int, db: Session = Depends(get_db)):
    students = db.query(models.Estudiante).\
        join(models.Inscripcion, models.Estudiante.estudiante_id == models.Inscripcion.estudiante_fk).\
        filter(models.Inscripcion.grupo_fk == grupo_id).all()
    return students



@app.get("/estudiantes/{student_id}/asignaturas_con_grupos", response_model=List[schemas.Subject_Group])
def get_student_subjects_with_groups(student_id: int, db: Session = Depends(get_db)):
    # First, find the program of the student
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Fetch all subjects for the student's program, including groups
    subjects = db.query(models.Asignatura).\
        options(joinedload(models.Asignatura.grupos)).\
        filter(models.Asignatura.programa_fk == student.estudiante_programa_fk).\
        all()

    return subjects


# Facultad endpoints

@app.post("/crear_facultad/", response_model=schemas.Facultad, status_code=status.HTTP_201_CREATED)
def create_faculty(facultad: schemas.FacultadCreate, db: Session = Depends(get_db)):
    return crud.create_facultad(db=db, facultad=facultad)


@app.get("/facultad/{faculty_id}", response_model=schemas.Facultad, status_code=status.HTTP_200_OK)
def read_faculty(faculty_id: int, db: Session = Depends(get_db)):
    db_faculty = crud.get_facultad(db, facultad_id=faculty_id)
    if db_faculty is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Faculty not found")
    return db_faculty


@app.get("/facultades/", response_model=List[schemas.Facultad])
def read_faculties(db: Session = Depends(get_db)):
    faculties = crud.get_all_facultad(db)
    return faculties


@app.patch("/actualizar_facultad/{faculty_id}", response_model=schemas.Facultad, status_code=status.HTTP_200_OK)
def update_faculty(faculty_id: int, faculty: schemas.FacultadUpdate, db: Session = Depends(get_db)):
    db_faculty = crud.update_facultad(db, faculty_id, faculty)
    if db_faculty is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Faculty not found")
    return db_faculty


@app.delete("/borrar_facultad/{faculty_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_faculty(faculty_id: int, db: Session = Depends(get_db)):
    success = crud.delete_facultad(db, faculty_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Faculty not found")
    return {"detail": "Faculty deleted successfully"}


# Programa Endpoints

@app.post("/crear_programa/", response_model=schemas.Programa, status_code=status.HTTP_201_CREATED)
def create_programa(programa: schemas.ProgramaCreate, db: Session = Depends(get_db)):
    return crud.create_programa(db=db, programa=programa)


@app.get("/programa/{programa_id}", response_model=schemas.Programa, status_code=status.HTTP_200_OK)
def read_programa(programa_id: int, db: Session = Depends(get_db)):
    db_programa = crud.get_programa(db, programa_id=programa_id)
    if db_programa is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Programa not found")
    return db_programa


@app.get("/programas/", response_model=List[schemas.Programa])
def read_programas(db: Session = Depends(get_db)):
    programas = crud.get_all_programa(db)
    return programas


@app.patch("/actualizar_programa/{programa_id}", response_model=schemas.Programa, status_code=status.HTTP_200_OK)
def update_programa(programa_id: int, programa: schemas.ProgramaUpdate, db: Session = Depends(get_db)):
    db_programa = crud.update_programa(db, programa_id, programa)
    if db_programa is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Programa not found")
    return db_programa


@app.delete("/borrar_programa/{programa_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_programa(programa_id: int, db: Session = Depends(get_db)):
    success = crud.delete_programa(db, programa_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Programa not found")
    return {"detail": "Programa deleted successfully"}


# Autenticacion Endpoints

@app.post("/login", response_model=schemas.LoginResponse)
def login(login: schemas.Login, db: Session = Depends(get_db)):

    db_user = db.query(models.Autenticacion).filter(models.Autenticacion.autenticacion_user == login.autenticacion_user).first()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")


    db_student_id = db.query(models.Estudiante).filter(models.Estudiante.estudiante_autenticacion_fk == db_user.aut_id).first()

    stored_hash = db_user.autenticacion_password.strip()

    login_password = login.autenticacion_password


    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode('utf-8')


    if bcrypt.checkpw(login_password.encode('utf-8'), stored_hash):
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={"message": "Password is correct", "student_id": db_student_id.estudiante_id, "rol": db_user.rol_fk}
        )
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password is incorrect")




@app.post("/crear_autenticacion/", response_model=schemas.Autenticacion, status_code=status.HTTP_201_CREATED)
def create_autenticacion(autenticacion: schemas.AutenticacionCreate, db: Session = Depends(get_db)):
    return crud.create_autenticacion(db=db, autenticacion=autenticacion)


@app.get("/autenticacion/{aut_id}", response_model=schemas.Autenticacion, status_code=status.HTTP_200_OK)
def read_autenticacion(aut_id: int, db: Session = Depends(get_db)):
    db_autenticacion = crud.get_autenticacion(db, aut_id=aut_id)
    if db_autenticacion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Autenticacion not found")
    return db_autenticacion


@app.get('/autenticaciones/', response_model=List[schemas.Autenticacion])
def read_autenticaciones(db: Session = Depends(get_db)):
    autenticaciones = crud.get_all_autenticacion(db)
    return autenticaciones


@app.patch("/actualizar_autenticacion/{auth_id}", response_model=schemas.Autenticacion, status_code=status.HTTP_200_OK)
def update_autenticacion(auth_id: int, autenticacion: schemas.AutenticacionUpdate, db: Session = Depends(get_db)):
    db_autenticacion = crud.update_autenticacion(db, auth_id, autenticacion)
    if db_autenticacion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Autenticacion not found")
    return db_autenticacion


@app.delete("/borrar_autenticacion/{auth_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_autenticacion(auth_id: int, db: Session = Depends(get_db)):
    success = crud.delete_autenticacion(db, auth_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Autenticacion not found")
    return {"detail": "Autenticacion deleted successfully"}

# Grupo Endpoints

@app.post("/crear_grupo/", response_model=schemas.Group, status_code=status.HTTP_201_CREATED)
def create_grupo(grupo: schemas.GroupCreate, db: Session = Depends(get_db)):
    return crud.create_grupo(db=db, grupo=grupo)


@app.get("/grupo/{grupo_id}", response_model=schemas.Group, status_code=status.HTTP_200_OK)
def read_grupo(grupo_id: int, db: Session = Depends(get_db)):
    db_grupo = crud.get_grupo(db, grupo_id=grupo_id)
    if db_grupo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo not found")
    return db_grupo


@app.get("/grupos/", response_model=List[schemas.Group])
def read_grupo(
    page_size: int = Query(10, alias="PageSize", gt=0),
    page_number: int = Query(1, alias="PageNumber", gt=0),
    sort_by: SortByGrupo = Query(SortByGrupo.grupo_name, alias="SortParameter.SortBy"),
    sort_direction: SortDirection = Query(SortDirection.desc, alias="SortParameter.SortDirection"),
    db: Session = Depends(get_db)):

    grupo_query = db.query(models.Grupo)

    if sort_direction == "asc":
        grupo_query = grupo_query.order_by(getattr(models.Grupo, sort_by.value).asc())
    else:
        grupo_query = grupo_query.order_by(getattr(models.Grupo, sort_by.value).desc())

    # Pagination logic
    offset = (page_number - 1) * page_size
    grupo_query = grupo_query.offset(offset).limit(page_size)

    # Execute query and fetch data
    grupos = grupo_query.all()

    return grupos


@app.patch("/actualizar_grupo/{grupo_id}", response_model=schemas.Group, status_code=status.HTTP_200_OK)
def update_grupo(grupo_id: int, grupo: schemas.GroupUpdate, db: Session = Depends(get_db)):
    db_grupo = crud.update_grupo(db, grupo_id, grupo)
    if db_grupo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo not found")
    return db_grupo


@app.delete("/borrar_grupo/{grupo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_grupo(grupo_id: int, db: Session = Depends(get_db)):
    success = crud.delete_grupo(db, grupo_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo not found")
    return {"detail": "Grupo deleted successfully"}


# Rol Endpoints

@app.post("/crear_rol/", response_model=schemas.Rol, status_code=status.HTTP_201_CREATED)
def create_rol(rol: schemas.RolCreate, db: Session = Depends(get_db)):
    return crud.create_rol(db=db, rol=rol)


@app.get("/rol/{rol_id}", response_model=schemas.Rol, status_code=status.HTTP_200_OK)
def read_rol(rol_id: int, db: Session = Depends(get_db)):
    db_rol = crud.get_rol(db, rol_id=rol_id)
    if db_rol is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol not found")
    return db_rol


@app.get("/roles/", response_model=List[schemas.Rol])
def read_roles(db: Session = Depends(get_db)):
    roles = crud.get_all_rol(db)
    return roles


@app.patch("/actualizar_rol/{rol_id}", response_model=schemas.Rol, status_code=status.HTTP_200_OK)
def update_rol(rol_id: int, rol: schemas.RolUpdate, db: Session = Depends(get_db)):
    db_rol = crud.update_rol(db, rol_id, rol)
    if db_rol is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol not found")
    return db_rol


@app.delete("/borrar_rol/{rol_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rol(rol_id: int, db: Session = Depends(get_db)):
    success = crud.delete_rol(db, rol_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol not found")
    return {"detail": "Rol deleted successfully"}


#Ingreso Fotos

def load_known_faces(bucket_name, start_photo_id, end_photo_id):

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    known_encodings = []
    known_usernames = []

    # Load only photos within the specified range
    for photo_id in range(start_photo_id, end_photo_id + 1):
        photo_name = f"photos/{photo_id}"
        print(photo_name)
        image_blob = bucket.blob(photo_name)
        image_bytes = image_blob.download_as_bytes()
        image = face_recognition.load_image_file(io.BytesIO(image_bytes))
        face_encodings = face_recognition.face_encodings(image)
        if face_encodings:
            known_encodings.append(face_encodings[0])
            known_usernames.append(str(photo_id))

    return known_usernames, known_encodings


@app.post("/login-by-face/")
async def login_by_face(photo: UploadFile = File(...)):
    base_dir = r"C:\Users\crist\Documentos\UPTC\10 SEMESTRE\SIMULACIÓN DE COMPUTADORES\API-main\API\fotos"
    file_location = os.path.join(base_dir, photo.filename)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_location), exist_ok=True)

    # Save the file
    file_data = await photo.read()

    with open(file_location, "wb") as file_object:
        file_object.write(file_data)

    
    # Load the image sent by the user
    user_image = face_recognition.load_image_file(io.BytesIO(file_data))
    user_face_encodings = face_recognition.face_encodings(user_image)

    if not user_face_encodings:
        raise HTTPException(status_code=400, detail="No faces detected in the image.")

    # Load known faces and their encodings from GCP
    print("POR AQUI 2")
    known_usernames, known_encodings = load_known_faces('fotos_sira', 12, 23)

    # Compare faces
    for username, known_encoding in zip(known_usernames, known_encodings):
        results = face_recognition.compare_faces([known_encoding], user_face_encodings[0], tolerance=0.6)
        if True in results:
            print("Welcome", username)
            return {"message": "Logged in successfully", "student_id": username}

    raise HTTPException(status_code=404, detail="No matching face found")


@app.post("/upload_photo/")
async def upload_photo(photo: UploadFile = File(...)):
    # Define the base directory
    base_dir = r"C:\Users\crist\Documentos\UPTC\10 SEMESTRE\SIMULACIÓN DE COMPUTADORES\API-main\API\fotos"
    file_location = os.path.join(base_dir, photo.filename)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_location), exist_ok=True)

    # Save the file
    with open(file_location, "wb") as file_object:
        file_object.write(await photo.read())

    return JSONResponse(content={"message": "File uploaded successfully", "file_path": file_location})



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8109)

