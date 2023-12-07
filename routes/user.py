from fastapi import APIRouter
from config.db import conn
from models.user import users
from schemas.user import User
from cryptography.fernet import Fernet

key = Fernet.generate_key()
f = Fernet(key)

user = APIRouter()

@user.get("/users")
def helloworld():
    return conn.execute(users.select()).fetchall()

@user.post("/users")
def create_user(user: User):
    new_user = {
        "name": user.name,
        "last_name": user.last_name,
        "username" : user.username,
        "password" : f.encrypt(user.password.encode("utf-8")),
        "is_active" : user.is_active,
        "role": user.role
    }
    print(new_user)
    return "Usuario"
