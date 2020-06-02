
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
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS

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

SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = 'http://petstore.swagger.io/v2/swagger.json'  # Our API url (can of course be a local resource)

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "Test application"
    },
    # oauth_config={  # OAuth config. See https://github.com/swagger-api/swagger-ui#oauth2-configuration .
    #    'clientId': "your-client-id",
    #    'clientSecret': "your-client-secret-if-required",
    #    'realm': "your-realms",
    #    'appName': "your-app-name",
    #    'scopeSeparator': " ",
    #    'additionalQueryStringParams': {'test': "hello"}
    # }
)

# Register blueprint at URL
# (URL must match the one given to factory function above)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
CORS(app)

@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)

from appsrc import route_users, model
#from appsrc import api_templates, route_bookedslots, route_bookableslots
from appsrc import route_addresses, route_openinghourstemplates, route_distributionowners, route_distributionpoints, route_recurringslotstemplates, route_covidtracking, route_bookableslots, route_bookedslots

#sapi_openinghoursdetails
#  api_openinghourstemplate, api_recurringslotstemplate,    