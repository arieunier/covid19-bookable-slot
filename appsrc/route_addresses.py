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


@app.route(variables.DEFAULT_API_URL + '/addresses',methods=['GET','POST'])
@login_required
def get_post_addresses():
    return route_generic.genericGetPostWithAuthentications("/addresses",current_user.is_authenticated)

@app.route(variables.DEFAULT_API_URL + '/addresses/<id_>',methods=['PUT', 'GET'])
@login_required
def get_put_addresses_byId(id_):
    return route_generic.genericGetPutDelById("/addresses/<id_>",current_user.is_authenticated, id_)
"""
@app.route(variables.DEFAULT_API_URL + '/addresses/<id_>',methods=['PUT', 'GET'])
@login_required
def get_put_addresses_byId(id_):
  try:
    logs.logger.debug("Authenticated -> {}-{} ".format(request.method, request.url))  
    logs.logger.debug(utils.get_debug_all(request))
    # use the end of the route to know which class the call is meant for
    properClassName = "addresses"
    properClass = Address
    logs.logger.debug("properclass={}".format(properClassName))

    if request.method == 'GET':
        noloadOptions=[]

        # retrieve what should be given within the body
        received_request = []
        try:
            if (request.json is not None):
                received_request = ujson.loads(request.json)
        except Exception as e:
            traceback.print_exc()

        request_filter=[]
        request_filter.append(properClass.id == id_)
        
        #load objects with or without children records
        objects = properClass.query.filter(and_(*request_filter)).options(noloadOptions).first_or_404()
        # if we are using an ad min then we will display all fields, if not .. then we will remove unnecessary fields
        result_dict = objects.serialize 
    elif request.method == 'PUT':
        # method is PUT
        # checks object exists
        objectExist = properClass.query.filter_by(id=id_).first_or_404()
        # retrieve what should be given within the body
        received_request = []
        try:
            if (request.json is not None):
                received_request = ujson.loads(request.json)
        except Exception as e:
            traceback.print_exc()
        # make sure values received in the body of the request are allowed
        utils.checkReceivedContentAgainstForbiddenValues(received_request, properClass.__curratedValue__ )
        #depending on unicity criteria for each object, check if this update can lead to a duplicate
        possibleDuplicates = utils.validateUnicityOnUpdate(properClass, received_request, id_)
        # now updates the field and flag it as modified for the orm
        for entry in received_request:
            logs.logger.debug("updating field ... {} --> {}".format(entry, received_request[entry]))
            objectExist.__dict__[entry] = received_request[entry]
            flag_modified(objectExist, entry)

        db.session.commit()
        result_dict = objectExist.serialize

    logs.logger.info(result_dict)

    return make_response(jsonify(result_dict), 200)
  except werkzeug.exceptions.NotFound as e:
    traceback.print_exc()
    return utils.returnResponse("Requested resource does not exist", 404)    
  except Exception as  e:
    traceback.print_exc()
    return utils.returnResponse("The server encountered an error while processing your request", 500)
"""
