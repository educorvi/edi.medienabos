from fastapi import FastAPI, HTTPException
from models import Abonnent, Abo, Base, ResultModel
from services import insert_abo_data, insert_subscriber_data
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
