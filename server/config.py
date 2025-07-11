import os

from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from datetime import timedelta
from dotenv import load_dotenv
from sqlalchemy import MetaData
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)


metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})
db = SQLAlchemy(metadata=metadata)
db.init_app(app)

migrate = Migrate(app, db)

api = Api(app)

CORS(app, 
     origins=["https://event-manager-flask-react-app.onrender.com", "http://127.0.0.1:3000"],
     supports_credentials=True,
     methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"]
    )