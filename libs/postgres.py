import variables
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()
MANUAL_ENGINE_POSTGRES = create_engine(variables.DATABASE_URL, pool_size=30, max_overflow=0)
Base.metadata.bind = MANUAL_ENGINE_POSTGRES
dbSession_postgres = sessionmaker(bind=MANUAL_ENGINE_POSTGRES)
session_postgres = dbSession_postgres()
