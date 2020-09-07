from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from bot import DATABASE_URL, LOGGER


def start() -> scoped_session:
  try:
    engine = create_engine(DATABASE_URL)
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False))
  except ValueError:
    LOGGER.error('Invalid DATABASE_URL : Exiting now.')
    exit(1)


BASE = declarative_base()
SESSION = start()