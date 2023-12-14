from pydantic import BaseModel
from typing import Optional

# Pydantic Model definition
class Result(BaseModel):
    id: Optional[str]
    fecha: Optional[str]
    hasParkinson: Optional[bool]
    resultext: Optional[str]
    result: Optional[bytes]
    probability: Optional[float]
    doctor: Optional[str]