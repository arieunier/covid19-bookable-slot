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

@app.route(variables.DEFAULT_API_URL + '/distributionowners/<id_>', methods=['GET'])
def get_unauthenticated_distributionowners_byId(id_):
    return route_generic.genericGetPutDelById("/distributionowners/<id_>",current_user.is_authenticated, id_)

@app.route(variables.DEFAULT_API_URL + '/distributionowners',methods=['GET','POST'])
@login_required
def get_post_distributionowners():
    return route_generic.genericGetPostWithAuthentications("/distributionowners",current_user.is_authenticated)

@app.route(variables.DEFAULT_API_URL + '/distributionowners/<id_>',methods=['PUT', 'GET'])
@login_required
def get_put_distributionowners_byId(id_):
    return route_generic.genericGetPutDelById("/distributionowners/<id_>",current_user.is_authenticated, id_)