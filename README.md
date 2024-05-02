1. Install

pip install fastapi uvicorn sqlalchemy pyodbc

2. Add the database models

models.py

3. Configure the data for the connection with the database SQL server

database.py

4. Configure the CRUD operations for the app

5. For run 

uvicorn main:app --reload
uvicorn main:app --host 0.0.0.0 --port 8109 --reload

