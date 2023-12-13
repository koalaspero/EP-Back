# medical_observation.py
from sqlalchemy import Table, Column, Integer, Text, Date, ForeignKey, MetaData
from config.db import meta, engine


MedicalObservation = Table(
    'MedicalObservation', meta,
    Column('id', Integer, primary_key=True),
    Column('observation', Text),
    Column('fecha', Date),
    Column('result', Integer, ForeignKey('Result.id'))
)