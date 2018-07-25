import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from jinja2 import Environment, PackageLoader, select_autoescape


app = Flask(__name__)


# Configs
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
app.config["UPLOAD_FOLDER"] = os.environ["UPLOAD_FOLDER"]
# TODO: Probably better to set on docker config, but for now leaving it to here


# TODO:  should probably throw errors if these are not set, just incase.

# URI:
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URI"]

db = SQLAlchemy(app)

env = Environment(
    loader=PackageLoader(__name__, 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

from models import Credentials
from routes import routes

migrate = Migrate(app, db)

routes(app, db, env)

if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True, port=80)
