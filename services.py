import os
import hashlib
import random
from models import Base, Abo, Subscriber, ResultModel
from sqlalchemy import create_engine, select, inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

database_file = 'user_data.db'
database_exists = os.path.isfile(database_file)
engine = create_engine(f'sqlite:///{database_file}')
Session = sessionmaker(bind=engine)

if not database_exists:
    Base.metadata.create_all(engine)

def generate_retcode(email):
    random_number = random.randint(10000, 99999)
    combined_string = f"{email}{random_number}"
    hash_object = hashlib.sha256(combined_string.encode())
    retcode = hash_object.hexdigest()
    return retcode

def send_subscriber_email(abo_data):
    print('in dieser Funktion wird die E-Mail gesendet')
    #TODO Implementierung einer Funktion für das Senden einer E-Mail

def insert_abo_data(abo_data):

    try:
        session = Session()
        user = Abo(**abo_data)
        session.add(user)
        session.commit()
        ret = ResultModel(httpstatus = 200,
                          message = "Ihre Daten wurden erfolgreich in unserer Datenbank gespeichert.")
        return ret

    except SQLAlchemyError as e:
        session.rollback()
        ret = ResultModel(httpstatus = 500, 
                          message = "Fehler bei der Speicherung Ihrer Daten, bitte versuchen Sie es zu einem späteren Zeitpunkt noch einmal",
                          errormessage = f"Failed to insert data {e}")
        return ret

    finally:
        if session:
            session.close()


def insert_subscriber_data(abo_data):

    session = Session()

    subscriber = session.query(Subscriber).filter(Subscriber.email == abo_data['email']).all()
    if subscriber:
        ret = ResultModel(httpstatus = 400,
                          message = """Für die angegebene E-Mail-Adresse wurde bereits ein Abonnement vorgemerkt. 
                                       Bitte prüfen Sie Ihr E-Mail-Postfach auf den Erhalt eines Bestätigungslinks""")
        return ret
    abonnent = session.query(Abo).filter(Abo.email == abo_data['email']).all()
    if abonnent:
        ret = ResultModel(httpstatus = 400,
                          message = """Für die angegebene E-Mail-Adresse existiert bereits ein Abonnement. 
                                       Für eventuelle Änderungen müssten wir Sie aus Sicherheitsgründen bitten, 
                                       Ihr Abonnement zunächst zu beenden und dann neu einzutragen.""")
        return ret
    retcode = generate_retcode(abo_data['email'])
    abo_data['retcode'] = retcode

    try:
        user = Subscriber(**abo_data)
        session.add(user)
        session.commit()
        send_subscriber_email(abo_data)
        ret = ResultModel(httpstatus = 200,
                          message = """Vielen Dank für Ihr Interesse an unserem Medienangebot.
                                       Wir haben Ihnen eine E-Mail mit einem Aktivierungslink
                                       an die von Ihnen angegebene E-Mail-Adresse gesendet.
                                       Bitte bestätigen Sie uns Ihr Abonnement durch Klick
                                       auf den Aktivierungslink.""",
                          retcode = retcode)
        return ret

    except SQLAlchemyError as e:
        session.rollback()
        ret = ResultModel(httpstatus = 500,
                          message = "Fehler bei der Speicherung Ihrer Daten, bitte versuchen Sie es zu einem späteren Zeitpunkt noch einmal",
                          errormessage = f"Failed to insert data {e}")
        return ret

    finally:
        if session:
            session.close()
