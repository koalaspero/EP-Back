from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from config.db import conn
from models.user import users
from schemas.user import User
from cryptography.fernet import Fernet
import jwt

key = Fernet.generate_key()
f = Fernet(key)

user = APIRouter()

def create_jwt_token(data: dict):
    expiration = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
    token_data = {"exp": expiration, **data}
    token = jwt.encode(token_data, key, algorithm="HS256")
    return token

@user.post("/token", tags=["authentication"])
def login_for_access_token(user_login):
    db_user = conn.execute(users.select().where(users.c.username == user_login.username)).first()
    if db_user and f.decrypt(db_user['password']).decode('utf-8') == user_login.password:
        token_data = {"sub": str(db_user[0]), "username": db_user[3]}
        access_token = create_jwt_token(token_data)
        cookies = {
            "id": db_user[0],
            "user_name" : db_user[3],
            "token" : access_token
        }
        return {"data": cookies}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@user.get("/users", tags=["users"])
def get_users():
    return conn.execute(users.select()).fetchall()

@user.get("/users/{id}", tags=["users"])
def get_user(id):

    db_object = conn.execute(users.select().where(users.c.id == id)).first()

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
        "password" : f.encrypt(user.password.encode("utf-8")),
        "is_active" : user.is_active,
        "role": user.role
    }

    result = conn.execute(users.insert().values(new_user))

    # Extract relevant data from the result
    inserted_user_id = result.lastrowid
    inserted_user = conn.execute(users.select().where(users.c.id == inserted_user_id)).first()

    cookies = {
        "id": inserted_user[0],
        "user_name" : inserted_user[3]
    }

    return cookies

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
        "password": f.encrypt(updated_user.password.encode("utf-8")),
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
