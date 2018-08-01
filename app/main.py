import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from jinja2 import Environment, PackageLoader, select_autoescape


app = Flask(__name__)


# Configs
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
app.config["UPLOAD_FOLDER"] = os.environ["UPLOAD_FOLDER"]

app.config["OAUTH_ENABLED"] = os.environ["OAUTH_ENABLED"]

if app.config["OAUTH_ENABLED"]:
    app.config["OAUTH_TOKEN_LINK"] = os.environ["OAUTH_TOKEN_LINK"]
    app.config["OAUTH_LOGIN_API"] = os.environ["OAUTH_LOGIN_API"]

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
