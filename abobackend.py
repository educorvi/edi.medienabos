from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from typing import Literal
from models import Abonnent, Abo, Base, RequestModel, ResultModel
from services import insert_abo_data, insert_subscriber_data, check_subscription, insert_marker_data
from services import check_marking, check_refresh, return_template, get_abo_data, update_abo_data
from datetime import datetime

app = FastAPI(
    title="Medienabonnements der BG ETEM",
    description="OpenAPI Services für die Abonnentenverwaltung",
    version="0.9btn (better than nothing)",
)

@app.get("/")
def welcome():
    return "BGETEM Abonnentenverwaltung"

@app.post("/{api_version}/abo", response_model=ResultModel)
def send_abonnement(api_version:str, data:Abonnent):
    """
    Serviceendpunkt für Benutzer:innen von per Login
    gesicherten Portalen, z.B. Versichertenportal, 
    Unternehmerportal.

    api_version - Version der API
    data - JSON-Objekt vom Typ Abonnent
    """
    if api_version == '0.9btn':
        datadict = vars(data) # wandelt das Object Abonnent in ein Dictionary
        now = datetime.now()
        datadict['refresh'] = now # ergänzt das Dict um den im Backend gebildeten Wert für refresh
        ret = insert_abo_data(datadict)
        return ret #Wir geben das Result-Model als Datenmodell zurück
    else:
        raise HTTPException(status_code=404, detail="api_version couldn't be found")

@app.post("/{api_version}/read_abonnent", response_model=Abonnent)
def read_abonnent(api_version:str, data:RequestModel):
    """
    Serviceendpunkt für Benutzer:innen von per Login
    gesicherten Portalen, z.B. Versichertenportal,
    Unternehmerportal.

    api_version - Version der API
    data - JSON-Objekt vom Typ Abonnent
    """
    if api_version == '0.9btn':
        ret = get_abo_data(data)
        return ret
    else:
        raise HTTPException(status_code=404, detail="api_version couldn't be found")

@app.post("/{api_version}/update_abonnent", response_model=ResultModel)
def update_abonnement(api_version:str, data:Abonnent):
    """
    Serviceendpunkt für Benutzer:innen von per Login
    gesicherten Portalen, z.B. Versichertenportal,
    Unternehmerportal.

    api_version - Version der API
    data - JSON-Objekt vom Typ Abonnent
    """
    if api_version == '0.9btn':
        datadict = vars(data) # wandelt das Object Abonnent in ein Dictionary
        now = datetime.now()
        datadict['refresh'] = now # ergänzt das Dict um den im Backend gebildeten Wert für refresh
        ret = update_abo_data(datadict)
        return ret #Wir geben das Result-Model als Datenmodell zurück
    else:
        raise HTTPException(status_code=404, detail="api_version couldn't be found")

@app.post("/{api_version}/subscribe", response_model=ResultModel)
def send_subscriber(api_version:str, data:Abonnent):
    """
    Serviceendpunkt für Benutzer:innen die über anonyme Portale, wie z.B.
    Website, Präventionsportale, Medienportal Medien abonnieren wollen.

    api_version - Version der API
    data - JSON-Objekt vom Typ Abonnent
    """
    if api_version == '0.9btn':
        datadict = vars(data) # wandelt das Object Abonnent in ein Dictionary
        now = datetime.now()
        datadict['refresh'] = now # ergänzt das Dict um den im Backend gebildeten Wert für refresh
        ret = insert_subscriber_data(datadict)
        return ret #Wir geben das Result-Model als Datenmodell zurück
    else:
        raise HTTPException(status_code=404, detail="api_version couldn't be found")

@app.get("/checksubscription/{retcode}", response_class=HTMLResponse)
def check_subscriber(retcode:str):
    """
    Serviceendpunkt für Benutzer:innen zur Bestätigung des Abonnements via Link
    """
    checker = check_subscription(retcode)
    if checker:
        return return_template(checker)
    else:
        raise HTTPException(status_code=404, detail="The returncode couldn't be found")

@app.post("/{api_version}/marker/{method}", response_model=ResultModel)
def send_marker(api_version:str, method:Literal['delete', 'update'], data:Abonnent):
    """
    Serviceendpunkt für Benutzer:innen die über anonyme Portale, wie z.B.
    Website, Präventionsportal kommen und ihr Abonnement löschen oder aktualisieren
    wollen.

    api_version - Version der API
    method - delete|update
    data - JSON-Object vom Typ Abonnent
    """
    if api_version == '0.9btn':
        datadict = vars(data)
        now = datetime.now()
        datadict['method'] = method
        datadict['refresh'] = now
        ret = insert_marker_data(datadict)
        return ret
    else:
        raise HTTPException(status_code=404, detail="api_version couldn't be found")

@app.get("/checkmarker/{retcode}", response_class=HTMLResponse)
def check_marker(retcode:str):
    """
    Serviceendpunkt für Benutzer:innen zur Bestätigung der Löschung oder Aktualisierung

    retcode - Returncode der vorher an die zur Vormerkung der Änderung versendet wurde
    """
    checker = check_marking(retcode)
    if checker:
        return return_template(checker)
    raise HTTPException(status_code=404, detail="The returncode couldn't be found")

@app.get("/refresher/{method}/{retcode}", response_class=HTMLResponse)
def refresh_abo(method:Literal['delete', 'refresh'], retcode:str):
    """
    Serviceendpunkt für Benutzer:innen zum Refresh oder zur Löschung des Abonnements

    method - delete|refresh
    retcode - returncode, der vorher per E-Mail ausgeliefert wurde
    """
    now = datetime.now()
    refresher = check_refresh(method, retcode, now)
    if refresher:
        return return_template(refresher)
    raise HTTPException(status_code=404, detail="The returncode couldn't be found")
