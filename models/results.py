# Import table definitions
from user import User
from medical_observation import MedicalObservation

# Define the Result table
from sqlalchemy import LargeBinary, Table, Column, Integer, Date, Text, DECIMAL, ForeignKey,SmallInteger
from config.db import meta, engine

Result = Table(
    'Result', meta,
    Column('id', Integer, primary_key=True),
    Column('fecha', Date),
    Column('hasParkinson', SmallInteger),
    Column('resultext', Text),
    Column('result', LargeBinary),  # Comma added here
    Column('probability', DECIMAL(10,2)),  # Comma added here
    Column('doctor', Integer, ForeignKey('User.id'))
)


# Create tables in the database
meta.create_all(engine)




