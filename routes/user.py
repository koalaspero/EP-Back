from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status
from models.user import users
from models.DBUser import DBUser
from schemas.user import User
from schemas.user_login import User_Login
from cryptography.fernet import Fernet
from routes.authentication import get_password_hash
import jwt
from config.db import (
    SessionLocal,
    Base,
)

# Define tu modelo de usuario (reemplaza esto con tu propio modelo)

key = Fernet.generate_key()
f = Fernet(key)


user = APIRouter()


@user.put("/users", tags=["users"])
def update_user(updated_user: User):
    # Check if the user with the specified ID exists
    db = SessionLocal()
    existing_user = db.query(DBUser).filter(DBUser.id == updated_user.id).first()

    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the username already exists for a different user
    username_exists = (
        db.query(DBUser).filter(DBUser.username == updated_user.username).first()
    )

    if username_exists and username_exists[0] != updated_user.id:
        raise HTTPException(
            status_code=409,
            detail="Username already exists",
        )
    updated_data = {
        "name": updated_user.name,
        "last_name": updated_user.last_name,
        "username": updated_user.username,
        "is_active": updated_user.is_active,
        "role": updated_user.role,
    }

    # Perform the update
    db.query(DBUser).filter(DBUser.id == updated_user.id).update(updated_data)

    # Retrieve and return the updated user
    updated_user_data = db.query(DBUser).filter(DBUser.id == updated_user.id).first()

    user_dict = {
        "id": str(updated_user_data[0]),
        "username": updated_user_data[3],
        "name": updated_user_data[1],
        "last_name": updated_user_data[2],
        "is_active": updated_user_data[5],
        "role": updated_user_data[6],
    }

    return {"data": user_dict}


@user.get("/users", tags=["users"])
def get_users():
    try:
        # Inicia una sesión de base de datos
        db = SessionLocal()

        # Realiza la consulta de usuarios dentro de la sesión
        users = db.query(DBUser).all()

        # Transforma los resultados en un formato deseado
        user_list = []
        for user in users:
            user_dict = {
                "id": user.id,
                "name": user.name,
                "last_name": user.last_name,
                "username": user.username,
                "role": user.role,
            }
            user_list.append(user_dict)

        # Cierra la sesión de base de datos
        db.close()

        return {"data": user_list}
    except Exception as e:
        # Si ocurre una excepción, realiza un rollback y maneja la excepción
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@user.get("/users/{id}", tags=["users"])
def get_user(id):
    db = SessionLocal()
    db_object = db.query(DBUser).filter(DBUser.id == id).first()

    if db_object is None:
        return {"error": "User not found"}  # or any appropriate response

    user_dict = {
        "id": str(db_object[0]),  # Assuming id is a string
        "username": db_object[3],
        "name": db_object[1],
        "last_name": db_object[2],
        "is_active": db_object[5],
        "role": db_object[6],
    }

    return {"data": user_dict}


@user.post("/users", tags=["users"])
def create_user(user: User):
    print(user)
    db = SessionLocal()
    existing_user = db.query(DBUser).filter(DBUser.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="User already exists",
        )
    new_user = {
        "name": user.name,
        "last_name": user.last_name,
        "username": user.username,
        "password": get_password_hash(user.password.encode("utf-8")),
        "is_active": user.is_active,
        "role": user.role,
    }
    result = db.execute(users.insert().values(new_user))
    db.commit()
    # Extract relevant data from the result
    inserted_user_id = result.lastrowid
    inserted_user = db.execute(
        users.select().where(users.c.id == inserted_user_id)
    ).first()

    data = {"id": inserted_user[0], "user_name": inserted_user[3]}

    return {"data": data}
