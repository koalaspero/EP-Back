from pydantic import BaseModel

class User_Login(BaseModel):
    username: str
    password: str
    role: int