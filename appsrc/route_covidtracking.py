from dataclasses import dataclass
from datetime import datetime,  timedelta
from flask import Flask, jsonify, make_response, request
from flask_sqlalchemy import SQLAlchemy
from appsrc import app, db
import uuid 
from libs import postgres, logs, utils, variables
import traceback
from sqlalchemy import or_, and_
import sqlalchemy
from sqlalchemy.orm.attributes import flag_modified
from appsrc.model import OpeningHoursTemplate, Address, DistributionOwner, DistributionPoint, BookableSlot, CovidTracking, BookedSlot, RecurringSlotsTemplate
import werkzeug
from flask_login import login_required, current_user
from sqlalchemy.orm import lazyload, noload
import ujson
from appsrc import route_generic


@app.route(variables.DEFAULT_API_URL + '/covidtracking',methods=['GET'])
@login_required
def get_covidtracking():
    logs.logger.debug("Authenticated -> {}-{} ".format(request.method, request.url))
    return route_generic.genericGetPost("/covidtracking",current_user.is_authenticated)


@app.route(variables.DEFAULT_API_URL + '/covidtracking', methods=['POST']) 
def post_covidtracking():   
    logs.logger.debug("Authenticated -> {}-{} ".format(request.method, request.url))
    return route_generic.genericGetPost("/covidtracking",current_user.is_authenticated)
