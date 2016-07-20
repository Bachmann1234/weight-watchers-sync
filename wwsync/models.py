from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

_Session = None


def get_db_session():
    global _Session
    if not _Session:
        engine = create_engine('sqlite:///wwsync.sqlite3')
        _Session = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)
    return _Session()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    fitbit_tokens = Column(String)
    ww_password = Column(String)
    ww_username = Column(String)
