import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)


# Configs
app.config["SECRET_KEY"]=os.environ["SECRET_KEY"]
app.config["UPLOAD_FOLDER"]=os.environ["UPLOAD_FOLDER"]
## TODO:  should probably throw errors if these are not set, just incase.

# URI:
app.config['SQLALCHEMY_DATABASE_URI']=os.environ["DATABASE_URI"]
 
db = SQLAlchemy(app)

from models import Credentials
from routes import routes

migrate = Migrate(app, db)

routes(app, db)

if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True, port=80)

