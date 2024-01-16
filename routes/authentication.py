from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from config.db import (
    SessionLocal,
    Base,
)
from models.user import users
from schemas.user import User
from schemas.user_login import User_Login
from schemas.token import TokenData, Token

SECRET_KEY = "6b71ee1ca968759605d4211f17c375c5"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 2

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="token")

auth = APIRouter()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(user_login: User_Login) -> Optional[User]:
    db = SessionLocal()
    db_object = db.execute(
        users.select().where((users.c.username == user_login.username))
    ).first()

    if db_object is None:
        return None  # User not found

    user = User(
        id=str(db_object[0]),  # Assuming id is a string
        username=db_object[3],
        name=db_object[1],
        last_name=db_object[2],
        password=db_object[4],
        is_active=db_object[5],
        role=int(db_object[6]),
    )
    return user


def authenticate_user(user_login: User_Login):
    user = get_user(user_login)

    if user is None or not verify_password(user_login.password, user.password):
        return False

    return user


def create_access_token(data: dict, expires_delta: timedelta or None = None):
    to_encode = data.copy()  # Fix: Call the copy method
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=2)

    to_encode.update({"exp": expire})  # Fix: Update the dictionary
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def get_current_user(token: str = Depends(oauth_2_scheme)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception

        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exception

    user = get_user(username=token_data.username)
    if user is None:
        raise credential_exception

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user


@auth.post("/token", response_model=Token, tags=["authentication"])
async def login_for_access_token(user_login: User_Login):
    user = authenticate_user(user_login)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    access_token = create_access_token(
        data={"username": user.username, "rol": user.role, "id": user.id},
        expires_delta=access_token_expires,
    )
    # print(access_token)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "id": user.id,
        "username": user.username,
    }


@auth.get("/auth/me", tags=["authentication"])
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@auth.get("/auth/me/items", tags=["authentication"])
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"id": current_user.id, "username": current_user.username}]


@auth.post("/auth/register", tags=["authentication"])
def register_user(user: dict):
    db = SessionLocal()
    print(user)
    # Check if the username already exists
    existing_user = db.execute(
        users.select().where(users.c.username == user["username"])
    ).first()
    if existing_user:
        return {"error": "Username already exists"}

    new_user = {
        "name": user["name"],
        "last_name": user["last_name"],
        "username": user["username"],
        "password": get_password_hash(user["password"].encode("utf-8")),
        "is_active": user["is_active"],
        "role": user["role"],
    }

    result = db.execute(users.insert().values(new_user))
    # get the id of the new user
    db.commit()
    user_id = result.lastrowid
    # print(access_token)
    access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    access_token = create_access_token(
        data={
            "username": new_user["username"],
            "rol": new_user["role"],
            "id": int(result.lastrowid),
        },
        expires_delta=access_token_expires,
    )
    print(access_token)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "id": int(result.lastrowid),
        "username": new_user["username"],
    }
