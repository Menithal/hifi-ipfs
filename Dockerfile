# Using Nginx + Python combo
# https://github.com/tiangolo/uwsgi-nginx-flask-docker
FROM tiangolo/uwsgi-nginx-flask:python3.6

LABEL author="Matti Lahtinen <menithal@norteclabs.com>"

# Installing ipfsapi (ipfs helper library), psycopg (psql adapter), and sqlalchemy (SQL Python ORM)
RUN pip install ipfsapi==0.4.3 flask_sqlalchemy==2.3.2 flask-marshmallow==0.9.0 Flask-Migrate==2.2.1 psycopg2-binary==2.7.5 python-dotenv==0.8.2
#Flask==1.0.2
# Now lets copy files to the directory.
COPY ./app /app