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
import pandas as pd
from io import BytesIO
from scipy.io import loadmat
import numpy as np
from tsfresh import extract_features, select_features
import joblib
from sklearn.preprocessing import StandardScaler
import csv

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
    name = res["fecha"] + res["extension"]
    source_file_data = bytes(res["source_file"].values())
    doctor_name = db.execute(users.select().where(users.c.id == res["doctor"])).first()
    new_res = {
        "fecha": res["fecha"],
        "hasParkinson": res["hasParkinson"],
        "resultext": res["resultext"],
        # "source_file": complete_path,
        "probability": res["probability"],
        "doctor": res["doctor"],
    }
    result = db.execute(ResultTB.insert().values(new_res))
    # get the id of the inserted row
    inserted_id = result.lastrowid
    name = res["fecha"] + "_" + str(inserted_id) + "."+res["extension"]

    file_path = "static/" + doctor_name.username + "/"
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    complete_path = file_path + name
    file = open(complete_path, "wb")
    file.write(source_file_data)
    file.close()
    db.commit()
    # actualizar el source_file con la ruta completa en la base de datos
    db.execute(
        ResultTB.update()
        .where(ResultTB.c.id == inserted_id)
        .values(source_file=complete_path)
    )
    # insertar la observacion medica
    db.commit()
    # Extract the ID of the inserted row
    db.close()
    if inserted_id:
        return {"state": "Registro exitoso", "id": inserted_id}
    else:
        raise HTTPException(status_code=500, detail="Error retrieving the inserted ID")


@result.post("/getResults", tags=["getResults"])
def obtain_initial_results(res: dict):
    tsfresh_df = pd.DataFrame(
        {
            "id": [],
            "time": [],
            "x": [],
            "y": [],
        }
    )
    tsfresh_data_list = []
    source_file_data = bytes(res["source_file"].values())
    csv_bytes = BytesIO(source_file_data)
    line = 0
    # check the file extension
    if res["extension"] == "svc":
        with csv_bytes as file:
            csv_text = file.read().decode("utf-8")
            csv_reader = csv.reader(csv_text.splitlines())
            for row in csv_reader:
                if line != 0:
                    numeros = row[0].split(" ")
                    print(numeros)
                    tsfresh_data_list.append(
                        {
                            "id": 1,
                            "time": int(numeros[2]),
                            "x": int(numeros[0]),
                            "y": int(numeros[1]),
                        }
                    )
                line = line + 1
    elif res["extension"] == "mat":
        data = loadmat(csv_bytes)
        thePoints = data["S"]["thePoints"][0][0]
        raw_timeSeries = data["S"]["Ts"][0][0][0]
        Sbuttons = data["S"]["Sbuttons"]
        x = thePoints[:, 0]
        y = thePoints[:, 1]
        length = len(Sbuttons[0][0])
        rule = raw_timeSeries[-1] / length
        finishTime = raw_timeSeries[-1]
        currenTimeSeries = np.transpose(
            np.arange(start=0, stop=raw_timeSeries[-1] + rule, step=rule)
        )
        if len(x) != len(currenTimeSeries) or len(y) != len(currenTimeSeries):
            currenTimeSeries = currenTimeSeries[1:]
        mask = (x != 683) & (y != 384)
        filtered_x = x[mask]
        filtered_y = y[mask]
        discarded_indices = np.where(~mask)[0]
        filtered_time = np.delete(currenTimeSeries, discarded_indices)
        for time, x, y in zip(filtered_time, filtered_x, filtered_y):
            tsfresh_data_list.append({"id": 1, "time": time, "x": x, "y": y})
    tsfresh_df = pd.concat(
        [tsfresh_df, pd.DataFrame(tsfresh_data_list)], ignore_index=True
    )
    tsfresh_df["id"] = tsfresh_df["id"].astype(int)
    tsfresh_df["x"] = tsfresh_df["x"].astype(int)
    tsfresh_df["y"] = tsfresh_df["y"].astype(int)
    extracted_features = extract_features(
        tsfresh_df, column_id="id", column_sort="time"
    )
    feature_order = [
        'x__change_quantiles__f_agg_"mean"__isabs_False__qh_1.0__ql_0.2',
        'x__change_quantiles__f_agg_"mean"__isabs_False__qh_0.8__ql_0.2',
        "x__mean_change",
        'x__change_quantiles__f_agg_"mean"__isabs_False__qh_1.0__ql_0.0',
        "x__time_reversal_asymmetry_statistic__lag_1",
        "x__time_reversal_asymmetry_statistic__lag_2",
        "x__time_reversal_asymmetry_statistic__lag_3",
        'y__change_quantiles__f_agg_"var"__isabs_False__qh_1.0__ql_0.0',
        'y__change_quantiles__f_agg_"mean"__isabs_True__qh_1.0__ql_0.0',
        "y__abs_energy",
        "y__minimum",
        "y__lempel_ziv_complexity__bins_100",
        'y__agg_linear_trend__attr_"intercept"__chunk_len_50__f_agg_"min"',
        "y__benford_correlation",
        "y__quantile__q_0.4",
        "y__c3__lag_3",
        "x__ratio_value_number_to_time_series_length",
        "y__sum_of_reoccurring_values",
        'y__agg_linear_trend__attr_"intercept"__chunk_len_5__f_agg_"mean"',
        "x__mean",
        "y__mean_n_absolute_max__number_of_maxima_7",
        "x__cid_ce__normalize_False",
        "x__first_location_of_maximum",
        "x__cwt_coefficients__coeff_8__w_20__widths_(2, 5, 10, 20)",
        "x__cwt_coefficients__coeff_9__w_10__widths_(2, 5, 10, 20)",
    ]
    extracted_features = extracted_features.loc[:, feature_order]
    # cargar el standard scaler que se guardo en el archivo svm/standard_scaler.pkl y escalar los datos
    scaler = joblib.load("svm/standard_scaler_25.pkl")
    values = scaler.transform(extracted_features)
    # create svm model with the pkd_svm.pkl file saved on svm/best_model_svm.pkl
    # and the extracted features
    model = joblib.load("svm/mejor_modelo_25_svm.pkl")
    # predict the probability of the parkinson
    probability = model.predict_proba(values)
    # probability in version 100%
    probability = probability * 100
    # get the probability of the parkinson
    result = model.predict(values)
    probability = probability[0][result]
    # redondear la probabilidad a dos decimales
    probability = round(probability[0], 2)
    # get the result of the prediction
    return {"result": str(result[0]), "probability": str(probability)}
