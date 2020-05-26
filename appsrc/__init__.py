
from flask import Flask
from libs import config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask.json import JSONEncoder
from libs import variables, logs, utils
import flask_login
from flask_login import LoginManager
import uuid
from flask_session import Session 
from datetime import timedelta
 


logs.logger_init(filename="app.log")


app = Flask(__name__, template_folder=variables.TEMPLATES_URL, static_folder=variables.STATIC_URL) 

app.config.from_object(config.config)
if (config.config.SESSION_TYPE =='redis' and config.config.SESSION_TYPE != ''):
    sess = Session()
    sess.permanent = False
    app.permanent_session_lifetime = timedelta(minutes=240) #4 hours lifetime
    sess.init_app(app)
    
login_manager = LoginManager()
login_manager.init_app(app)
db = SQLAlchemy(app)
#migrate = Migrate(app, db)


utils.initDatabase(db)
from appsrc import api_templates, routeusers, model

#sapi_openinghoursdetails
#  api_openinghourstemplate, api_recurringslotstemplate,