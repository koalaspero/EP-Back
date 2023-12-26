from fastapi import APIRouter, HTTPException
from sqlalchemy import desc
from models.results import Result as ResultTB
from schemas.results import Result as Result
from models.user import users
from models.medical_observation import MedicalObservation as MedicalDB
from config.db import (
    SessionLocal,
    Base,
)
import base64  # Importa la biblioteca base64
from dataclasses import dataclass
from fastapi import FastAPI, Form, Depends, UploadFile
from starlette.responses import HTMLResponse
import os

result = APIRouter()


@result.get("/results", tags=["results"])
def get_results():
    db = SessionLocal()
    result = db.execute(ResultTB.select()).fetchall()
    list = []
    for row in result:
        doctor = db.execute(users.select().where(users.c.id == row[6])).first()
        observation = db.execute(
            MedicalDB.select().where(MedicalDB.c.result == row[0])
        ).all()
        observation_list = []
        for obs in observation:
            observation_list.append(obs[1])
        source_file = row[4]
        dict = {
            "id": str(row[0]),
            "fecha": row[1],
            "hasParkinson": bool(row[2]),
            "resultext": row[3],
            "source_file": source_file,
            "probability": row[5],
            "doctor": doctor.username,
            "observation": observation_list,
        }

        list.append(dict)

    return {"data": list}


@result.get("/results/{id}", tags=["results"])
def get_result(id):
    db = SessionLocal()
    db_object = db.execute(ResultTB.select().where(ResultTB.c.id == id)).first()

    if db_object is None:
        return {"error": "Result not found"}  # or any appropriate response

    dict = {
        "id": str(db_object[0]),
        "fecha": db_object[1],
        "hasParkinson": bool(db_object[2]),
        "resultext": db_object[3],
        "source_file": db_object[4],
        "probability": db_object[5],
        "doctor": str(db_object[6]),
    }

    return {"data": dict}


@result.post("/results", tags=["results"])
def create_result(res: dict):
    db = SessionLocal()
    name = res["fecha"] + ".csv"
    source_file_data = bytes(res["source_file"].values())
    file_path = "static/" + name
    file = open(file_path, "wb")
    file.write(source_file_data)
    file.close()
    # where the file is stored
    res["source_file"] = file_path
    # get the doctor name
    doctor_name = db.execute(users.select().where(users.c.id == res["doctor"])).first()
    # create the file path if doesn't exist
    file_path = "static/" + doctor_name.username + "/"
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    complete_path = file_path + name
    file = open(complete_path, "wb")
    file.write(source_file_data)
    file.close()
    print(res)
    new_res = {
        "fecha": res["fecha"],
        "hasParkinson": res["hasParkinson"],
        "resultext": res["resultext"],
        "source_file":complete_path,
        "probability": res["probability"],
        "doctor": res["doctor"],
    }

    result = db.execute(ResultTB.insert().values(new_res))
    db.commit()
    # Extract the ID of the inserted row
    inserted_id = result.lastrowid
    db.close()
    if inserted_id:
        return {"state": "Registro exitoso", "id": inserted_id}
    else:
        raise HTTPException(status_code=500, detail="Error retrieving the inserted ID")
