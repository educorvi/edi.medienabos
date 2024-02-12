from typing import Optional, List, Dict, Text, Union, Literal
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Table(Base):
    __abstract__ = True 

    id = Column(Integer, primary_key=True, autoincrement=True)
    untnr = Column(String, nullable=True)
    anrede = Column(String, nullable=False)
    titel = Column(String, nullable=True)
    vorname = Column(String, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    versand_name = Column(String, nullable=True)
    versand_strhnr = Column(String, nullable=True)
    versand_plz = Column(String, nullable=True)
    versand_ort = Column(String, nullable=True)
    etem = Column(Integer, nullable=False)
    profi = Column(Integer, nullable=False)
    medien = Column(JSON, nullable=True)
    refresh = Column(DateTime, nullable=False)

class Abo(Table):
    __tablename__ = 'abonnements'

class Subscriber(Table):
    __tablename__ = 'subscribers'

    retcode = Column(String, nullable=False)

class Marker(Table):
    __tablename__ = 'markers'

    retcode = Column(String, nullable=False)
    method = Column(String, nullable=False)

class Refresher(Table):
    __tablename__ = 'refreshers'

    retcode = Column(String, nullable=False)

class Abonnent(BaseModel):
    """
    Datenmodell für die Abonnementverwaltung
    """
    untnr: Optional[str] = Field(title=u"Unternehmensnummer", default=None)
    anrede: Literal['Frau', 'Herr', 'keine Anrede'] = Field(title="Anrede")
    titel: Optional[Literal["Dr.", "Prof."]] = Field(title="Akademischer Titel", default=None)
    vorname : str = Field(title=u"Vorname des Verantwortlichen für die Applikation")
    name : str = Field(title=u"Name des Verantwortlichen für die Applikation")
    email : EmailStr = Field(title=u"Versandadresse: E-Mail-Adresse")
    versand_name : Optional[str] = Field(title="Versandadresse: Abweichender Name oder Firmenname", default=None)
    versand_strhnr : Optional[str] = Field(title=u"Versandadresse: Straße und Hausnummer", default=None)
    versand_plz : Optional[str] = Field(title=u"Versandadresse: Postleitzahl, optional inkl. Länderkennung, z.B. DE-90763", default=None)
    versand_ort : Optional[str] = Field(title=u"Versandadresse: Ort", default=None)
    etem : int = Field(title="Anzahl der Abonnements der Zeitschrift etem", default=0) 
    profi : int = Field(title="Anzahl der Abonnements der Zeitschrift profi", default=0) 
    medien : dict = Field(title="Dictionary mit Angaben zu den abonnierten Medien")

class ResultModel(BaseModel):
    """
    Datenmodell für die Rückgabe an den Frontend
    """
    httpstatus: int = Field(title=u"HTTP-Statuscode")
    message: str = Field(title=u"Nachricht für den Frontend zur Einblendung für die Benutzer:innen")
    errormessage: Optional[str] = Field(title=u"Errormessage bzw. serverseitige Exception zur Information des Frontend-Administrators", default=None)
    retcode: Optional[str] = Field(title=u"Returncode zur Auslieferung an die Benutzer:innen z.B. zum Check der E-Mail", default=None)
