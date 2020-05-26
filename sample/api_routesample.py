
from dataclasses import dataclass
from datetime import datetime
from flask import Flask, jsonify, make_response, request
from flask_sqlalchemy import SQLAlchemy
from model import brand, company
from app import app
from libs import postgres, logs, utils


@app.route('/api/sample/brands/',methods=['GET'])
def brands():
  try:
    logs.logger.debug(utils.get_debug_all(request))
    if (not utils.checkAuthorization(request)):
      return utils.returnResponse("Unauthorized access", 401)

    objects = brand.query.all()
    result_dict =  [ item.serialize for item in objects ]
    logs.logger.info(result_dict)
    return make_response(jsonify(result_dict), 200)
  except Exception as e:
    import traceback
    traceback.print_exc()
    return utils.returnResponse("The server encountered an error while processing your request", 500)


@app.route('/api/sample/brands/<id_>', methods=['GET'])
def brandById(id_):
  try:
    logs.logger.debug(utils.get_debug_all(request))
    if (not utils.checkAuthorization(request)):
      return utils.returnResponse("Unauthorized access", 401)

    objects = brand.query.filter_by(id=id_).first_or_404()
    result_dict =  objects.serialize
    logs.logger.info(result_dict)
    return make_response(jsonify(result_dict), 200)
  except Exception as  e:
    import traceback
    traceback.print_exc()
    return utils.returnResponse("The server encountered an error while processing your request", 500)

@app.route('/api/sample/companies/',methods=['GET'])
def companies():
  try:
    logs.logger.debug(utils.get_debug_all(request))
    if (not utils.checkAuthorization(request)):
      return utils.returnResponse("Unauthorized access", 401)

    objects = company.query.all()
    result_dict =  [ item.serialize for item in objects ]
    logs.logger.info(result_dict)
    return make_response(jsonify(result_dict), 200)
  except Exception as e:
    import traceback
    traceback.print_exc()
    return utils.returnResponse("The server encountered an error while processing your request", 500)