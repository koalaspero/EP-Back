# medical_observation.py
from sqlalchemy import Table, Column, Integer, Text, Date, ForeignKey
from sqlalchemy import create_engine, MetaData
from models.results import Result

engine = create_engine("mysql+pymysql://root:@localhost:3306/ep_db")
meta = MetaData()


MedicalObservation = Table(
    'MedicalObservation', meta,
    Column('id', Integer, primary_key=True),
    Column('observationText', Text),
    Column('result', Integer, ForeignKey(Result.c.id))
)

# Create tables in the database
meta.create_all(engine)