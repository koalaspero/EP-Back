from sqlalchemy import Boolean, Integer, SmallInteger, String, Table,Column
from sqlalchemy import create_engine, MetaData

# from config.db import meta, engine

engine = create_engine("mysql+pymysql://root:@localhost:3306/ep_db")

meta = MetaData()


users = Table("users", meta, 
              Column("id", Integer, primary_key= True), 
              Column("name", String(50)),
              Column("last_name", String(50)),
              Column("username", String(255)),
              Column("password", String(255)),
              Column("is_active", Boolean),
              Column("role", SmallInteger))


meta.create_all(engine)