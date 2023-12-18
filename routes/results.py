from fastapi import APIRouter, HTTPException
from sqlalchemy import desc
from config.db import conn
from models.results import Result as ResultTB
from schemas.results import Result as Result

result = APIRouter()

@result.get("/results", tags=["results"])
def get_results():
    result = conn.execute(ResultTB.select()).fetchall()

    list = []

    for row in result:

        dict = {
            "id": str(row[0]),
            "fecha": row[1],
            "hasParkinson": bool(row[2]),
            "resultext": row[3],
            "source_file": row[4],
            "probability": row[5],
            "doctor": str(row[6]),
        }

        list.append(dict)

    return {"data": list}

@result.get("/results/{id}", tags=["results"])
def get_result(id):

    db_object = conn.execute(ResultTB.select().where(ResultTB.c.id == id)).first()

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

    new_res = {
        "fecha": res['fecha'],
        "hasParkinson": res['hasParkinson'],
        "resultext": res['resultext'],
        "source_file": bytes(res['source_file'].values()),
        "probability": res['probability'],
        "doctor": res['doctor']
    }

    result = conn.execute(ResultTB.insert().values(new_res))

    # Extract the ID of the inserted row
    inserted_id = result.lastrowid

    if inserted_id:
        return {"state": "Registro exitoso", "id": inserted_id}
    else:
        raise HTTPException(status_code=500, detail="Error retrieving the inserted ID")