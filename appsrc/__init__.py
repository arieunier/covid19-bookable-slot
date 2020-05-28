
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
from flasgger import Swagger


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
swagger = Swagger(app)
#migrate = Migrate(app, db)


from appsrc import route_users, model
#from appsrc import api_templates, route_bookedslots, route_bookableslots
from appsrc import route_addresses, route_openinghourstemplates, route_distributionowners, route_distributionpoints, route_recurringslotstemplates, route_covidtracking, route_bookableslots, route_bookedslots

#sapi_openinghoursdetails
#  api_openinghourstemplate, api_recurringslotstemplate,    