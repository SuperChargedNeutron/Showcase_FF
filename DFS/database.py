
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

dir_path = os.path.abspath(os.path.dirname('__file__'))
DB_PATH = os.path.join(dir_path, 'Resources', 'fantasy_stats.db')

SQLALCHEMY_DATABASE_URL = f"sqlite+pysqlite:////{DB_PATH}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()