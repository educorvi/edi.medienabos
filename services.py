import os
import hashlib
import random
from models import Base, Abo, Subscriber, Abonnent, ResultModel, Marker, Refresher
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


def send_marker_email(abo_data):
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


def get_abo_data(request_data):
    
    session = Session()
    email = request_data.email
    abonnent = session.query(Abo).filter(Abo.email == email).first()
    if abonnent:
        datadict = vars(abonnent)
        del datadict['id']
        del datadict['_sa_instance_state']
        return Abonnent(**datadict)
    session.close()


def update_abo_data(abo_data):

    session = Session()
    email = abo_data['email']
    abonnent = session.query(Abo).filter(Abo.email == email).first()
    if abonnent:
        try:
            for key, value in abo_data.items():
                setattr(abonnent, key, value)
            session.commit()
            ret = ResultModel(httpstatus = 200,
                              message = "Ihre Daten wurden erfolgreich in unserer Datenbank gespeichert.")
        except SQLAlchemyError as e:
            session.rollback()
            ret = ResultModel(httpstatus = 500,
                          message = "Fehler bei der Speicherung Ihrer Daten, bitte versuchen Sie es zu einem späteren Zeitpunkt noch einmal",
                          errormessage = f"Failed to insert data {e}")

        finally:
            return ret
            if session:
                session.close()

    ret = ResultModel(httpstatus = 500,
                      message = "Fehler bei der Aktualisierung Ihrer Daten, bitte versuchen Sie\
                                 es zu einem späteren Zeitpunkt noch einmal",
                      errormessage = f"Abonnent entry not found in database.")


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


def check_subscription(retcode):

    session = Session()
    subscriber = session.query(Subscriber).filter(Subscriber.retcode == retcode).first()
    session.close()
    if subscriber:
        datadict = vars(subscriber)
        del datadict['id']
        del datadict['retcode']
        del datadict['_sa_instance_state']
        data = insert_abo_data(datadict)
        if data.httpstatus == 200:
            return 'thankyou'
    return False


def insert_marker_data(marker_data):

    session = Session()
    marker = session.query(Marker).filter(Marker.email == marker_data['email']).all()
    if marker:
        ret = ResultModel(httpstatus = 400,
                          message = """Für die angegebene E-Mail-Adresse wurde bereits eine Änderungsmitteilung vorgemerkt 
                                       Bitte prüfen Sie Ihr E-Mail-Postfach auf den Erhalt eines Bestätigungslinks""")
        session.close()
        return ret
    
    abonnent = session.query(Abo).filter(Abo.email == marker_data['email']).all()
    if not abonnent:
        message = "Für die von Ihnen angegebene E-Mail-Adresse existiert aktuell kein Medienabonnement"
        ret = ResultModel(httpstatus = 400,
                          message = message)
        session.close()
        return ret

    retcode = generate_retcode(marker_data['email'])
    marker_data['retcode'] = retcode

    message_delete = """Wir haben Ihren Wunsch zur Beendigung des Abonnenments vorgemerkt. Sie erhalten
                        jetzt eine E-Mail mit einem Bestätigungslink. Bitte klicken Sie auf den Link
                        um die Beendigung Ihres Abonnements zu bestätigen."""

    message_update = """Wir haben Ihren Wunsch zur Aktualisierung des Abonnements vorgemerkt. Sie erhalten
                        jetzt eine E-Mail mit einem Bestätigungslink. Bitte klicken Sie auf den Link
                        um die Aktualisierung Ihres Abonnements zur bestätigen."""

    try:
        user = Marker(**marker_data)
        session.add(user)
        session.commit()
        send_marker_email(marker_data)
        if marker_data['method'] == 'delete':
            message = message_delete
        else:
            message = message_update
        ret = ResultModel(httpstatus = 200,
                          message = message,
                          retcode = retcode)
        return ret

    except SQLAlchemyError as e:
        session.rollback()
        ret = ResultModel(httpstatus = 500,
                          message = "Fehler bei der Speicherung Ihrer Daten, bitte versuchen Sie es\
                                     zu einem späteren Zeitpunkt noch einmal",
                          errormessage = f"Failed to insert data {e}")
        return ret

    finally:
        if session:
            session.close()


def check_marking(retcode):

    session = Session()
    marker = session.query(Marker).filter(Marker.retcode == retcode).first()
    if marker:
        email = marker.email
        method = marker.method
        datadict = vars(marker)
        object_to_delete = session.query(Abo).filter(Abo.email == email).first()
        if object_to_delete:
            session.delete(object_to_delete)
        session.delete(marker)
        session.commit()
        session.close()
        del datadict['id']
        del datadict['retcode']
        del datadict['method']
        del datadict['_sa_instance_state']
        if method == 'update':
            data = insert_abo_data(datadict)
            if data.httpstatus == 200:
                return method
        elif method == 'delete':
            return method
    return False

def check_refresh(method, retcode, now):
    """
    Die E-Mail für check_refresh wird aus einem Cron-Script heraus erzeugt, das
    jeden Tag einmal läuft und alte Abos in die Refresh-Tabelle kopiert um zu
    signalisieren, dass diese Datenbankeinträge auf eine Auffrischung warten.
    """
    session = Session()
    #refresher = session.query(Refresher).filter(Refresher.retcode == retcode).first()
    #email = refresher.email
    email = 'lwalther@novareto.de'
    original = session.query(Abo).filter(Abo.email == email).first()
    if method == 'delete':
        if original:
            session.delete(original)
            #session.delete(refresher)
            session.commit()
            session.close()
            return method
    elif method == 'refresh':
        original.refresh = now
        session.commit()
        session.close()
        return method   
    return False

def return_template(method):
    path = os.path.dirname(__file__)
    path += f'/templates/{method}.html'
    file = open(path, 'rb')
    htmltext = file.read().decode('utf-8')
    return htmltext
