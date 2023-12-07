from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: Optional[str] = None
    username: str
    password: str
    name: str
    last_name: str
    is_active: bool
    role: int


