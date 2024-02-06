Installation
------------

### Python-Installation (Ubuntu)

    ~/$ sudo apt-get install build-essential python-dev libjpeg-dev libxslt-dev supervisor
    ~/$ sudo apt-get install libpython3-dev
    ~/$ sudo apt-get install python3-pip

### FastApi-Installation mit edi.medienabos

    ~/$ git clone ...edi.medienabos.git
    ~/$ cd edi.medienabos
    ~/edi.medienabos$ python3 -m venv env
    ~/edi.medienabos$ source ./env/bin/activate
    ~/edi.medienabos$ pip install -r requirements.txt

### Starten und Stoppen des API-Servers im Entwicklungsmodus

    ~/edi.medienabos$ uvicorn abobackend:app --reload
    [CTRL-C]

Deployment für den Produktionsbetrieb
-------------------------------------

Für den Produktionsbetrieb wird eine Supervisor-Konfiguration mit einem vorgeschalteten NGINX-Server
empfohlen. Mit den folgenden Konfigurationsdateien kann eine solche Installation realisiert werden.

### Supervisor Konfiguration 

/etc/supervisor/conf.d/medienabos.conf

    [fcgi-program:uvicorn]
    socket=tcp://127.0.0.1:8000
    command=/home/{your_home}/edi.medienabos/env/bin/uvicorn --fd 0 --app-dir /home/{your_home}/edi.medienabos abobackend:app
    numprocs=4
    process_name=uvicorn-%(process_num)d
    stdout_logfile=/dev/stdout
    stdout_logfile_maxbytes=0

### NGINX Konfiguration

/etc/nginx/sites-available/medienabos.conf

	upstream abos {
    	server 127.0.0.1:8000;
	}

	server {
    	server_name medienabos.uv-kooperation.de;
    	client_max_body_size 4G;
    	access_log /var/log/nginx/medienabos.de.access.log;
    	error_log /var/log/nginx/medienabos.de.error.log;

   		location / {
      		proxy_set_header Host $http_host;
      		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      		proxy_set_header X-Forwarded-Proto $scheme;
      		proxy_redirect off;
      		proxy_buffering off;
     		proxy_pass http://abos;
    	}


    	listen 80;

	}

Ansprechpartner / Maintainer
----------------------------

Lars Walther (lars.walther@educorvi.de)

Lizenz
------

FastAPI ist unter den Bedingungen der MIT lizensiert.
Urheber der Software ist Sebastian Ramirez 
E-Mail: tiangolo@gmail.com
WWW: https://tiangolo.com

Für edi.medienabos gelten ebenfalls die Bedingungen der MIT-Lizenz

Copyright (c) 2004-2024 educorvi GmbH & Co. KG
lars.walther@educorvi.de

Weitere Quellen
---------------
