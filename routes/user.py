from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from config.db import conn
from models.user import users
from schemas.user import User
from schemas.user_login import User_Login
from cryptography.fernet import Fernet
from routes.authentication import get_password_hash
import jwt

key = Fernet.generate_key()
f = Fernet(key)


user = APIRouter()

@user.get("/users", tags=["users"])
def get_users():
    result = conn.execute(users.select()).fetchall()

    user_list = []
    for row in result:
        user_dict = {
            "id": str(row[0]),
            "name": row[1],
            "last_name": row[2],
            "username": row[3],
            "password": row[4],
            "is_active": row[5],
            "role": row[6]
        }
        user_list.append(user_dict)

    return {"data": user_list}

@user.get("/users/{id}", tags=["users"])
def get_user(id):

    db_object = conn.execute(users.select().where(users.c.id == id)).first()

    if db_object is None:
        return {"error": "User not found"}  # or any appropriate response
    
    user_dict = {
        "id": str(db_object[0]),  # Assuming id is a string
        "username": db_object[3],
        "name": db_object[1],
        "last_name": db_object[2],
        "is_active": db_object[5],
        "role": db_object[6]
    }

    return {"data": user_dict}

@user.post("/users", tags=["users"])
def create_user(user: User):

    # Check if the username already exists
    existing_user = conn.execute(users.select().where(users.c.username == user.username)).first()
    if existing_user:
        return {"error": "Username already exists"}

    new_user = {
        "name": user.name,
        "last_name": user.last_name,
        "username" : user.username,
        "password" : get_password_hash(user.password.encode("utf-8")),
        "is_active" : user.is_active,
        "role": user.role
    }

    result = conn.execute(users.insert().values(new_user))

    # Extract relevant data from the result
    inserted_user_id = result.lastrowid
    inserted_user = conn.execute(users.select().where(users.c.id == inserted_user_id)).first()

    data = {
        "id": inserted_user[0],
        "user_name" : inserted_user[3]
    }

    return {"data" : data}

@user.put("/users/{id}", tags=["users"])
def update_user(id: int, updated_user: User):
    # Check if the user with the specified ID exists
    existing_user = conn.execute(users.select().where(users.c.id == id)).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update user data
    updated_data = {
        "name": updated_user.name,
        "last_name": updated_user.last_name,
        "username": updated_user.username,
        "password": get_password_hash(updated_user.password.encode("utf-8")),
        "is_active": updated_user.is_active,
        "role": updated_user.role
    }

    # Perform the update
    conn.execute(users.update().where(users.c.id == id).values(updated_data))

    # Retrieve and return the updated user
    updated_user_data = conn.execute(users.select().where(users.c.id == id)).first()

    user_dict = {
        "id": str(updated_user_data[0]),
        "username": updated_user_data[3],
        "name": updated_user_data[1],
        "last_name": updated_user_data[2],
        "is_active": updated_user_data[5],
        "role": updated_user_data[6]
    }

    return {"data": user_dict}
