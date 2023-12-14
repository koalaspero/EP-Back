from pydantic import BaseModel
from typing import Optional
from sqlalchemy import DECIMAL, Date

# Pydantic Model definition
class MedicalObservation(BaseModel):
    id: Optional[str]
    observationText: str
    result: Optional[str]