# Define the Result table
from sqlalchemy import LargeBinary, Table, Column, Integer, Date, Text, DECIMAL, ForeignKey,SmallInteger
from sqlalchemy import create_engine, MetaData
from models.user import users

engine = create_engine("mysql+pymysql://root:@localhost:3306/ep_db")

meta = MetaData()

Result = Table(
    'Result', meta,
    Column('id', Integer, primary_key=True),
    Column('fecha', Date),
    Column('hasParkinson', SmallInteger),
    Column('resultext', Text),
    Column('source_file', Text),  # Comma added here
    Column('probability', DECIMAL(10,2)),  # Comma added here
    Column('doctor', Integer, ForeignKey(users.c.id))
)
try:
    # Attempt to create tables in the database
    meta.create_all(engine)
    print("Tables created successfully!")
except Exception as e:
    print(f"Error creating tables: {e}")




