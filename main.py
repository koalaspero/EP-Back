from fastapi import FastAPI
from routes.user import user

app = FastAPI()

app.include_router(user)

# class User(BaseModel):
#     id: int
#     user_name: str
#     password: str
#     name: str
#     last_name: str

# @app.get("/")
# def index():
#     return {"mensaje": "Hey, hola mundillo"}

# @app.get("/users/{username}")
# def mostar_user(username):
#     return {"data": username}

# @app.post("/users")
# def insertar_libros(user: User):
#     return {"message": f"Usuario {user.user_name} registrado"}