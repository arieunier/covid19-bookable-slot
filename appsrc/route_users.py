
from flask_login import current_user, login_user, logout_user
from appsrc.model import User
from appsrc import login_manager        
from libs import utils, logs, variables
from flask import Flask, jsonify, make_response, request
from appsrc import app, db

@login_manager.user_loader
def load_user(id):
    return User.query.get(str(id))

@app.route(variables.DEFAULT_API_URL + '/logout')
def logout():
    logout_user()
    return utils.returnResponse(jsonify("Goodbye Marilou"), 200)


@app.route(variables.DEFAULT_API_URL + '/login', methods=['GET', 'POST'])
def login():
    logs.logger.debug(utils.get_debug_all(request))

    if current_user.is_authenticated:
        return utils.returnResponse(jsonify({"Error" : "You are already authenticated, logout first"}), 404)        

    hasAuthorizationHeader, decodedHeader = utils.checkAuthorization(request)
    if (not hasAuthorizationHeader ):
      return utils.returnResponse("Unauthorized access", 401)

    #U/P are given in the authorization header
    decodedHeaderSplitted=decodedHeader.decode('utf-8').split(':')

    user = User.query.filter_by(username=decodedHeaderSplitted[0]).first()
    if user is None or not user.check_password(decodedHeaderSplitted[1]):
        return utils.returnResponse(jsonify({"Error" : "incorrect login or password"}), 404) 

    login_user(user)
    return utils.returnResponse(jsonify("Welcome to the matrix neo"), 200)
    