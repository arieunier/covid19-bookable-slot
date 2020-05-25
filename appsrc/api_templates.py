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
from model import RecurringSlotsTemplate, OpeningHoursTemplate, Address, DistributionOwner, DistributionPoint, BookableSlot, CovidTracking, BookedSlot
import werkzeug
from flask_login import login_required, current_user
from sqlalchemy.orm import lazyload, noload
import ujson


# will be used by the functions bellow to dynamically use the proper classes. Most of the code has the same logic
classLoader =  {
    "openinghourstemplates" : OpeningHoursTemplate, 
    "recurringslotstemplates" : RecurringSlotsTemplate ,
    "addresses": Address, 
    "distributionowners" : DistributionOwner,
    "distributionpoints" : DistributionPoint,
    "bookablelots" : BookableSlot,
    "bookedslots": BookedSlot,
    'covidtracking': CovidTracking 
    }   


##### UN  AUTHENTICATED ENDPOINTS
@app.route('/api/covid19/distributionowners/<id_>', methods=['GET'])
@app.route('/api/covid19/distributionpoints/<id_>', methods=['GET'])
@app.route('/api/covid19/bookableslots/<id_>', methods=['GET', 'DEL'])
@app.route('/api/covid19/bookedslots/<id_>', methods=['DEL', 'GET'])
def unauthenticatedRoutesGetOrPutOrDelById(id_):
  logs.logger.debug("UNAuthenticated -> {}-{} ".format(request.method, request.url))
  return __getOrPutOrDelById(current_user.is_authenticated, id_)

@app.route('/api/covid19/distributionpoints', methods=['GET'])
@app.route('/api/covid19/bookedslots', methods=['POST'])
@app.route('/api/covid19/covidtracking', methods=['POST'])
def unauthenticatedRoutesGetOrPostAll():
  logs.logger.debug(current_user.is_authenticated)
  logs.logger.debug("UNAuthenticated -> {}-{} ".format(request.method, request.url))
  return __getOrPostAll(current_user.is_authenticated)


##### AUTHENTICATED ENDPOINTS

def __getOrPostAll(isAdmin):
  try:
    logs.logger.debug(utils.get_debug_all(request))
    
    url_splitted=request.url.split('/')
    properClassName = url_splitted[len(url_splitted) - 1 ].split('?')[0] #in case there's an attribute
    properClass = classLoader[properClassName]
    logs.logger.debug("properclass={}".format(properClassName))

    # check method type
    if request.method == 'GET':
      request_filter = []
      for entry in request.args:
        if ((request.args.get(entry) != None) & (request.args.get(entry) != '')):
          logs.logger.debug(entry)
          request_filter.append(properClass.__dict__[entry] == (request.args.get(entry) ))

      noloadOptions=[]
      if (isAdmin == False): #we wont load unecessary data 
        for entry in properClass.__publicNoLoadOptions__:
          noloadOptions.append(noload(entry))

      if (len(properClass.__publicNoLoadOptions__) > 0):
        objects = properClass.query.filter(and_(*request_filter)).options(noloadOptions).all()
      else:
        objects = properClass.query.filter(and_(*request_filter)).all()

      if (isAdmin):
        result_dict =  [ item.serialize for item in objects ]
      else:
        result_dict =  [ item.serialize_public for item in objects ]
    else:
      try:
        if (request.json == None):
          raise Exception('Request is empty')
        # checks content, name can't be null
        received_request = utils.currateDictValue(ujson.loads(request.json), properClass.__curratedValue__ )
        # check that there is not another openinghourstemplate with this name    
        utils.checkObjectUnicity(properClass, received_request)
        if (properClassName == "bookedslots"):
          # test if there is enough room for this slot
          bookableSlot =  BookableSlot.query.filter_by(id=received_request['refBookableSlotId']).options(noloadOptions).first_or_404()
          if (not ((bookableSlot.currentCapacity + received_request['numberOfPerson']) <= bookableSlot.maxCapacity)):
            raise Exception("Not enough remaining place at this slot. Please select another one or reduce the number of person in the group")
          # test if the same person did not book on the same day in the same distribution point
          bookableSlotDay = datetime.strptime(bookableSlot.dateStart.strftime(strftime(variables.DATE_PATTERN),variables.DATE_PATTERN))
          nextDay = bookableSlotDay + timedelta(days=1)
          filtersQueryAnd = []
          filtersQueryAnd.append(BookableSlot.dateStart == bookableSlotDay) #no during current day
          filtersQueryAnd.append(BookableSlot.dateStart < nextDay) #before next day
          filtersQueryAnd.append(refDistributionPointId == received_request['refDistributionPointId']) #same distribution
          filtersQueryOr = []
          filtersQueryOr.append(BookableSlot.email == received_request['email'])
          filtersQueryOr.append(BookableSlot.telephone == received_request['telephone'])
          checkDuplicates = BookableSlot.query.filter(and_(*filtersQueryAnd)).filter(or_(*filtersQueryOr)).all()
          if  checkDuplicates.count() != 0 :
            for entry in checkDuplicates:
              logs.logger.error("Duplicate entry found with {}".format(entry))
            raise Exception("A similar booking has been made with same information on the same day.")
          # generates a unique code
          unique_code = uuid.uuid4().__str__()[:8]
          # adds it
          newTemplate = properClass(id=uuid.uuid4().__str__(),
            firstname = received_request['firstname'],
            lastname = received_request['lastname'],
            telephone = received_request['telephone'],
            email = received_request['email'],
            numberOfPerson = received_request['numberOfPerson'],
            confirmationCode = unique_code,
            status = "booked",
            refBookableSlotId = received_request['refBookableSlotId'],
            refDistributionPointId = received_request['refDistributionPointId'])
          db.session.add(newTemplate)
          # updates current capacity at the bookable slot
          bookableSlot.currentCapacity += received_request['numberOfPerson']
          flag_modified(bookableSlot, 'numberOfPerson')
        elif (properClassName ==' covidtracking'):
          # checks the distribution poitn exists
          checkDistributionPoint = DistributionPoint.query.filter_by(id=received_request['refDistributionPoint']).first_or_404()
          # insert it
          newTempate = properClass(id = uuid.uuid4().__str__(),
               firstname = received_request['firstname'],
            lastname = received_request['lastname'],
            telephone = received_request['telephone'],
            email = received_request['email'],
            numberOfPerson = received_request['numberOfPerson'],
            refDistributionPointId = received_request['refDistributionPointId'])

        elif (properClassName == "distributionowners"):            
            newTemplate = properClass(id = uuid.uuid4().__str__(),
                name = received_request['name'], 
                description=received_request['description'],
                logoUrl=received_request['logoUrl'],
                telephone=received_request['telephone'],
                email=received_request['email'],
                refAddressId=received_request['refAddressId'],
            )
        elif (properClassName == "distributionpoints"):            
            newTemplate = properClass(id = uuid.uuid4().__str__(),
                name = received_request['name'], 
                description=received_request['description'],
                logoUrl=received_request['logoUrl'],
                telephone=received_request['telephone'],
                email=received_request['email'],
                maxCapacity=received_request['maxCapacity'],
                refDistributionOwnerId=received_request['refDistributionOwnerId'],
                refRecurringSlotsTemplateId=received_request['refRecurringSlotsTemplateId'],
                refAddressId=received_request['refAddressId'],
            )  
        elif (properClassName == 'openinghourstemplates'):
            newTemplate = properClass(id = uuid.uuid4().__str__(), 
                name = received_request['name'], 
                description=received_request['description'],
                mon=received_request['mon'],
                tue=received_request['tue'],
                wed=received_request['wed'],
                thu=received_request['thu'],
                fri=received_request['fri'],
                sat=received_request['sat'],
                sun=received_request['sun'])
        elif (properClassName == 'recurringslotstemplates'):
                newTemplate = properClass(id = uuid.uuid4().__str__(), 
                name = received_request['name'], 
                description=received_request['description'],
                slotLength=received_request['slotLength'],
                slotCapacity=received_request['slotCapacity']
                )
        elif (properClassName == "addresses"):
                newTemplate = properClass( id = uuid.uuid4().__str__(), 
                number = received_request['number'],
                street = received_request['street'],
                zipcode = received_request['zipcode'],
                city = received_request['city'],
                country = received_request['country'],
                state = received_request['state'] 
                )
  
                  
        db.session.add(newTemplate)
        db.session.commit()
        if (isAdmin):
          result_dict = newTemplate.serialize
        else:
          result_dict = newTemplate.serialize_public
      except Exception as e:
        traceback.print_exc()
        return utils.returnResponse(jsonify({'Error':e.__str__()}), 500)

    logs.logger.info(result_dict)
    return make_response(jsonify(result_dict), 200)

  except werkzeug.exceptions.NotFound as e:
    traceback.print_exc()
    return utils.returnResponse("Requested resource does not exist", 404)        
  except Exception as e:
    traceback.print_exc()
    return utils.returnResponse("The server encountered an error while processing your request", 500)

def __getOrPutOrDelById(isAdmin, id_):
  try:
    # use the end of the route to know which class the call is meant for
    url_splitted=request.url.split('/')
    properClassName = url_splitted[len(url_splitted) - 2 ]
    properClass = classLoader[properClassName]
    logs.logger.debug("properclass={}".format(properClassName))


    if request.method == 'GET':
      noloadOptions=[]
      if (isAdmin == False): #we wont load unecessary data so we use the publicnoload attribut to avoid loading children records
        for entry in properClass.__publicNoLoadOptions__:
          noloadOptions.append(noload(entry))
      # this route has a specific behavior for bookable slots & covid tracking, so we make sure we're not in on of these context
      if (properClassName not in ['bookableslots', 'covidtracking']):
        request_filter=[]
        request_filter.append(properClass.id == id_)
        # if object is a bookedslot, then the confirmationcode must be given also in the request
        if (properClassName == 'bookedslots'):
          if ('confirmationCode' not in request.args ):
            raise Exception("Error, confirmation code is mandatory to display a booked slot.")
          else:
            request_filter.append(properClass.confirmationCode == request.args.get('confirmationCode'))
        
        #load objects with or without children records
        objects = properClass.query.filter(and_(*request_filter)).options(noloadOptions).first_or_404()
        # if we are using an admin then we will display all fields, if not .. then we will remove unnecessary fields
        if (isAdmin):
          try:
            result_dict = [ item.serialize for item in objects ]
          except TypeError:
            result_dict = objects.serialize
        else:
          try:
            result_dict = [ item.serialize_public for item in objects ]
          except TypeError:
            result_dict = objects.serialize_public           
      else:
        # these tow routes can have more param sgiven in the url
        request_filter = []
        # both covid tracking & bookable slots endpoints are using the distribution id as filter
        request_filter.append(properClass.refDistributionId == id_)
        if ( properClassName == 'bookableslots'):  # bookable slot api has a specific field for filtering
          if ('dateStart' not in request.args ):
            request_filter.append(properClass.dateStart >= datetime.datetime.now())
          else:
            request_filter.append(properClass.dateStart >= request.args.get('dateStart'))

        # pass all attributes received in the and filter. 
        for entry in request.args:
          if ((request.args.get(entry) != None) & (request.args.get(entry) != '')):
            logs.logger.debug(entry)
            request_filter.append(properClass.__dict__[entry] == (request.args.get(entry) ))


        objects = properClass.query.filter(and_(*request_filter)).all()
        if (isAdmin):
          result_dict = objects.serialize
        else:
          result_dict = objects.serialize_public
    elif request.method == 'PUT':
      # method is PUT
      # checks object exists
      objectExist = properClass.query.filter_by(id=id_).first_or_404()
      # retrieve what should be given within the body
      received_request = ujson.loads(request.json)
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
      if (isAdmin):
        result_dict = objectExist.serialize
      else:
        result_dict = objectExist.serialize_public
    
    
    else: #DEL WARNiNG
      #del
      logs.logger.info('delete detected')
      # two cases for delete : bookedlosts or bookableslots
      # make sure we have ALL the proper params, ie : bookableslot id + code given as part of the request
      
      request_filter = []
      if (properClassName == 'bookedslot'):
        request_filter.append(properClass.id == received_request['id'])
        request_filter.append(properClass.confirmationCode == received_request['confirmationCode'])
        BookedSlots.query.filter(and_(*request_filter)).delete()
      else: # can only be bookableslots as per routes
        #loads it
        bSlot = BookableSlot.query.filter_by(id=id_)
        if len(bSlot.bookedSlots > 0 ):
          raise Exception("Can't delete this bookable slot. Some people ({})already registered.".format(len(bSlot.bookedSlots)))
        else:
          bSlot.delete()

      db.session.commit()

      result_dict=[{'Result':'Object deleted successfully'}]
    logs.logger.info(result_dict)

    return make_response(jsonify(result_dict), 200)
  except werkzeug.exceptions.NotFound as e:
    traceback.print_exc()
    return utils.returnResponse("Requested resource does not exist", 404)    
  except Exception as  e:
    traceback.print_exc()
    return utils.returnResponse("The server encountered an error while processing your request", 500)


@app.route('/api/covid19/distributionowners',methods=['GET','POST'])
@app.route('/api/covid19/openinghourstemplates',methods=['GET','POST'])
@app.route('/api/covid19/recurringslotstemplates',methods=['GET','POST'])
@app.route('/api/covid19/addresses',methods=['GET', 'POST'])
@app.route('/api/covid19/distributionpoints', methods=['POST'])
@login_required
def authenticatedRoutesGetOrPostAll():
  logs.logger.debug("Authenticated -> {}-{} ".format(request.method, request.url))
  return __getOrPostAll(current_user.is_authenticated)


@app.route('/api/covid19/distributionowners/<id_>', methods=['PUT'])
@app.route('/api/covid19/openinghourstemplates/<id_>', methods=['GET', 'PUT'])
@app.route('/api/covid19/recurringslotstemplate/<id_>', methods=['GET', 'PUT'])
@app.route('/api/covid19/addresses/<id_>', methods=['GET', 'PUT'])
@app.route('/api/covid19/distributionpoints/<id_>', methods=['PUT'])
@app.route('/api/covid19/covidtracking/<id_>', methods=['GET'])
@login_required
def authenticatedRoutesGetOrPutById(id_):
  logs.logger.debug("Authenticated -> {}-{} ".format(request.method, request.url))
  return __getOrPutOrDelById(current_user.is_authenticated, id_)
