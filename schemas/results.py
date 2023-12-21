from pydantic import BaseModel
from typing import Optional
from fastapi import FastAPI, Form, Depends, UploadFile


# Pydantic Model definition
class Result(BaseModel):
    id: Optional[str]
    fecha: Optional[str]
    hasParkinson: Optional[bool]
    resultext: Optional[str]
    source_file: UploadFile = Form(...)
    probability: Optional[float]
    doctor: Optional[str]
