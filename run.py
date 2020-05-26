from flask import Flask
import json
from app import app, db
from libs import logs, variables

import  uuid
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False, port=int(variables.WEBPORT))