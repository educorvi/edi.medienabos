import os
from models import Base, Abo
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

database_file = 'user_data.db'
database_exists = os.path.isfile(database_file)
engine = create_engine(f'sqlite:///{database_file}')
Session = sessionmaker(bind=engine)

if not database_exists:
    Base.metadata.create_all(engine)

class DatabaseError(Exception):
    """Exception wird bei Datenbankfehlern geworfen"""
    pass


def insert_abo_data(abo_data):

    try:
        session = Session()
        user = Abo(**abo_data)
        session.add(user)
        session.commit()
        return abo_data

    except SQLAlchemyError as e:
        session.rollback()
        raise DatabaseError(f"Failed to insert data {e}")

    finally:
        if session:
            session.close()
