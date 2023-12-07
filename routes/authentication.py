from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from config.db import conn
from models.user import users
from schemas.user import User
from schemas.user_login import User_Login
from cryptography.fernet import Fernet
import jwt

key = Fernet.generate_key()
f = Fernet(key)

auth = APIRouter()

# def create_jwt_token(data: dict):
#     expiration = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
#     token_data = {"exp": expiration, **data}
#     token = jwt.encode(token_data, key, algorithm="HS256")
#     return token

@auth.post("/auth/login", tags=["authentication"])
def login_for_access_token(user_login: User_Login):
    print(user_login)
    db_user = conn.execute(users.select().where(users.c.username == user_login.username)).first()
    if db_user and f.decrypt(db_user[4]).decode('utf-8') == user_login.password:
        # token_data = {"sub": str(db_user[0]), "username": db_user[3]}
        # access_token = create_jwt_token(token_data)
        cookies = {
            "id": db_user[0],
            "user_name" : db_user[3],
            # "token" : access_token
        }
        return {"data": cookies}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
@auth.post("/auth/register",  tags=["authentication"])
def register_user(user: User):

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

    # token_data = {"sub": str(inserted_user[0]), "username": inserted_user[3]}
    # access_token = create_jwt_token(token_data)
    
    cookies = {
        "id": inserted_user[0],
        "user_name" : inserted_user[3],
        # "token" : access_token
    }

    return {"data" : cookies}


