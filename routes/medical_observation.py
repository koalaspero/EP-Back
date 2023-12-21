from fastapi import APIRouter, HTTPException
from config.db import (
    SessionLocal,
    Base,
)
from models.medical_observation import MedicalObservation as MedicalDB
from schemas.medical_observation import MedicalObservation

medical_observation = APIRouter()


@medical_observation.get("/meds", tags=["Medical Observations"])
def get_meds():
    db = SessionLocal()
    meds = db.execute(MedicalDB.select()).fetchall()

    list = []

    for row in meds:
        dict = {"id": str(row[0]), "observationText": row[1], "result": row[2]}

        list.append(dict)

    return {"data": list}


@medical_observation.get("/meds/{id}", tags=["Medical Observations"])
def get_med(id):
    db = SessionLocal()
    db_object = db.execute(MedicalDB.select().where(MedicalDB.c.id == id)).first()

    if db_object is None:
        return {"error": "Result not found"}  # or any appropriate response

    dict = {
        "id": str(db_object[0]),  # Assuming id is a string
        "observationText": db_object[1],
        "result": db_object[2],
    }

    return {"data": dict}


@medical_observation.post("/meds", tags=["Medical Observations"])
def create_meds(med: dict):
    db = SessionLocal()
    new_ob = {
        "observationText": med["observationText"],
        "result": med["result"],
    }

    db.execute(MedicalDB.insert().values(new_ob))
    db.commit()
    return {"state": "Observacion añadida"}
