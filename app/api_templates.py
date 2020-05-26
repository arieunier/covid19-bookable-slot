from dataclasses import dataclass
from datetime import datetime,  timedelta
from flask import Flask, jsonify, make_response, request
from flask_sqlalchemy import SQLAlchemy
from app import app, db
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
    "bookableslots" : BookableSlot,
    "bookedslots": BookedSlot,
    'covidtracking': CovidTracking 
    }   


##### UNAUTHENTICATED ENDPOINTS
@app.route(variables.DEFAULT_API_URL + '/distributionowners/<id_>', methods=['GET'])
@app.route(variables.DEFAULT_API_URL + '/distributionpoints/<id_>', methods=['GET'])
@app.route(variables.DEFAULT_API_URL + '/bookableslots/<id_>', methods=['GET', 'DELETE'])
@app.route(variables.DEFAULT_API_URL + '/bookedslots/<id_>', methods=['DELETE', 'GET', 'PUT'])
def unauthenticatedRoutesGetOrPutOrDelById(id_):
  logs.logger.debug("UNAuthenticated -> {}-{} ".format(request.method, request.url))
  return __getOrPutOrDelById(current_user.is_authenticated, id_)

@app.route(variables.DEFAULT_API_URL + '/distributionpoints', methods=['GET'])
@app.route(variables.DEFAULT_API_URL + '/bookedslots', methods=['POST'])
@app.route(variables.DEFAULT_API_URL + '/covidtracking', methods=['POST'])
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
      #if distribution point is given, it is mandatory to add in parameter the refDistributionOwnerId
      if (properClassName == 'distributionpoints'):
        if (not 'refDistributionOwnerId' in request.args or request.args.get('refDistributionOwnerId') == '' or  request.args.get('refDistributionOwnerId') == None):
          raise Exception('Error: refDistributionOwnerId is mandatory when accessing this route')
        #checks given distribution point exist
        utils.checksReferencesId(properClass, request.args)
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
        received_request = []
        try:
          if (request.json is not None):
            received_request = ujson.loads(request.json)
        except Exception as e:
          traceback.print_exc()

        received_request = utils.currateDictValue(ujson.loads(request.json), properClass.__curratedValue__ )
        # check that there is not another objet with same information     
        utils.checkObjectUnicity(properClass, received_request)
        utils.checksReferencesId(properClass, received_request)      
        if (properClassName == "bookedslots"):
          # test if there is enough room for this slot
          bookableSlot =  BookableSlot.query.filter_by(id=received_request['refBookableSlotId']).first_or_404()
          if (not ((bookableSlot.currentCapacity - received_request['numberOfPerson']) >= 0 )):
            raise Exception("Not enough remaining place ({}) at this slot. Please select another one or reduce the number of person ({}) in the group. ".format(bookableSlot.currentCapacity,
          received_request['numberOfPerson']))
          # test if the same person did not book on the same day in the same distribution point
          bookableSlotDay = datetime.strptime(bookableSlot.dateStart.strftime(variables.DATE_PATTERN),variables.DATE_PATTERN)
          
          nextDay = bookableSlotDay + timedelta(days=1)
          logs.logger.info("Interval Dates {} - {}".format(bookableSlotDay,  nextDay))

          filtersQueryAnd = [] #BookableSlot
          filtersQueryAnd.append(BookableSlot.dateStart >= bookableSlotDay) #no during current day
          filtersQueryAnd.append(BookableSlot.dateStart < nextDay) #before next day
          filtersQueryAnd.append(BookableSlot.refDistributionPointId == received_request['refDistributionPointId']) #same distribution
          
          filtersQueryOr = [] #BookedSlot
          filtersQueryOr.append(BookedSlot.email == received_request['email'])
          filtersQueryOr.append(BookedSlot.telephone == received_request['telephone'])
          checkDuplicates = db.session.query(BookedSlot).filter(or_(*filtersQueryOr)).join(BookableSlot).filter(and_(*filtersQueryAnd)).all()

          #checkDuplicates = BookableSlot.query.filter(and_(*filtersQueryAnd)).filter(or_(*filtersQueryOr)).all()
          if  len(checkDuplicates) != 0 :
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
          bookableSlot.currentCapacity -= received_request['numberOfPerson']
          flag_modified(bookableSlot, 'currentCapacity')
        elif (properClassName =='covidtracking'):
          newTemplate = properClass(id = uuid.uuid4().__str__(),
               firstname = received_request['firstname'],
            lastname = received_request['lastname'],
            telephone = received_request['telephone'],
            email = received_request['email'],
            numberOfPerson = received_request['numberOfPerson'],
            refDistributionPointId = received_request['refDistributionPointId'])
        elif (properClassName == "distributionowners"):      
            utils.checksReferencesId(properClass, received_request)      
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
              refOpeningHoursTemplateId=received_request['refOpeningHoursTemplateId'],              
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
    logs.logger.debug(utils.get_debug_all(request))
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
        # retrieve what should be given within the body
        received_request = []
        try:
          if (request.json is not None):
            received_request = ujson.loads(request.json)
        except Exception as e:
          traceback.print_exc()

        request_filter=[]
        request_filter.append(properClass.id == id_)
        # if object is a bookedslot, then the confirmationcode must be given also in the request
        if (properClassName == 'bookedslots'):
          if ('confirmationCode' not in received_request ):
            raise Exception("Error, confirmation code is mandatory to display a booked slot.")
          else:
            request_filter.append(properClass.confirmationCode == received_request['confirmationCode'])
        
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
        # these tow routes can have more param given in the url
        request_filter = []
        # both covid tracking & bookable slots endpoints are using the distribution id as filter, given in the url
        # first checks the ref id given
        utils.checksReferencesId(properClass, {"refDistributionPointId":id_})      
        request_filter.append(properClass.refDistributionPointId == id_)

        if ( properClassName == 'bookableslots'):  # bookable slot api has a specific field for filtering
          if ('dateStart' not in request.args ):
            request_filter.append(properClass.dateStart >= utils.getCurrentDay())
          else:
            request_filter.append(properClass.dateStart >= utils.getDateFromStr(request.args.get('dateStart'), variables.DATE_PATTERN))
        elif (properClassName == 'covidtracking'):
           if ('dateStart' not in request.args ):
            request_filter.append(properClass.created_on >= utils.getCurrentDay())
            request_filter.append(properClass.created_on <= utils.getTomorrowDT())
           else:
             request_filter.append(properClass.created_on >= utils.getDateFromStr(request.args.get('dateStart'), variables.DATE_PATTERN))
             request_filter.append(properClass.created_on <= (utils.getDateFromStr(request.args.get('dateStart'), variables.DATE_PATTERN) + timedelta(days=1)))

        # pass all attributes received in the and filter. 
        for entry in request.args:
          if ((request.args.get(entry) != None) & (request.args.get(entry) != '')):
            logs.logger.debug(entry)
            #be carefull if it is a date, do not pass it, it's done already for bookableslots
            if (entry != 'dateStart'):
              request_filter.append(properClass.__dict__[entry] == (request.args.get(entry) ))


        objects = properClass.query.filter(and_(*request_filter)).all()
        if (isAdmin):
          result_dict = [ item.serialize for item in objects ]
        else:
          result_dict = [ item.serialize_public for item in objects ] #objects.serialize_public
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
      if (properClassName == 'bookedslots'):
        if ('confirmationCode' not in received_request ):
          raise Exception("Error, confirmation code is mandatory to update a booked slot.")
        #checks the combinaison uid/code
        request_filter=[]          
        request_filter.append(properClass.id == id_)
        request_filter.append(properClass.confirmationCode == received_request['confirmationCode'])
        originalBslot  = BookedSlot.query.filter(and_(*request_filter)).first_or_404()

        # tricky part
        # presence of refBookableSlotId / refDistributionPointId will imply more checks. We will forbid these changes and reject, asking to delete the slot
        currentRefBookableSlotId = originalBslot.refBookableSlotId
        currentRefDistributionPointId = originalBslot.refDistributionPointId
        if (('refBookableSlotId' in received_request and received_request['refBookableSlotId'] != currentRefBookableSlotId) 
          or ('refDistributionPointId' in received_request and received_request['refDistributionPointId'] != currentRefDistributionPointId)):
          raise Exception("Error: Changing refBookableSlotId or refDistributionPointId is forbidden, delete bookedlost and recreate it.")
        
        #if we change the number of person, or , we must check there is enough room
        previousNbPerson = originalBslot.numberOfPerson
        if (('numberOfPerson' in received_request and received_request['numberOfPerson'] !=  previousNbPerson)):
          newValue = received_request['numberOfPerson']
          # gets bookable slot
          bookableSlot = BookableSlot.query.filter_by(id=originalBslot.refBookableSlotId).first_or_404()
          newCapacity = bookableSlot.currentCapacity + previousNbPerson - newValue
          logs.logger.info("old/newCapacity -> {}/{}".format(bookableSlot.currentCapacity, newCapacity))
          if (not newCapacity >= 0):
            raise Exception("Error: there isn't enough room left for this number of person.")
          else:
            bookableSlot.currentCapacity = newCapacity
            flag_modified(bookableSlot, 'currentCapacity')
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
      received_request = []
      request_filter = []
      if (properClassName == 'bookedslots'):
        received_request = []
        try:
          if (request.json is not None):
            received_request = ujson.loads(request.json)
        except Exception as e:
          traceback.print_exc()

        request_filter.append(properClass.id == id_)
        request_filter.append(properClass.confirmationCode == received_request['confirmationCode'])
        bSlot = BookedSlot.query.filter(and_(*request_filter)).first_or_404()
        #increase capacity of related bookable slot
        currentNbOfPerson = bSlot.numberOfPerson
        # gets bookable slot
        bookableSlot = BookableSlot.query.filter_by(id=bSlot.refBookableSlotId).first_or_404()
        newCapacity = bookableSlot.currentCapacity + currentNbOfPerson 
        logs.logger.info("old/newCapacity -> {}/{}".format(bookableSlot.currentCapacity, newCapacity))
        bookableSlot.currentCapacity = newCapacity
        flag_modified(bookableSlot, 'currentCapacity')
        logs.logger.info("newCapacity -> {}".format(newCapacity))
           
        db.session.delete(bSlot)
        
      else: # can only be bookableslots as per routes
        #loads it
        bSlot = BookableSlot.query.filter_by(id=id_).first()
        if len(bSlot.bookedSlots) > 0:
          raise Exception("Can't delete this bookable slot. Some people ({}) are already registered.".format(len(bSlot.bookedSlots)))
        else:
          db.session.delete(bSlot)

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


@app.route(variables.DEFAULT_API_URL + '/distributionowners',methods=['GET','POST'])
@app.route(variables.DEFAULT_API_URL + '/openinghourstemplates',methods=['GET','POST'])
@app.route(variables.DEFAULT_API_URL + '/recurringslotstemplates',methods=['GET','POST'])
@app.route(variables.DEFAULT_API_URL + '/addresses',methods=['GET', 'POST'])
@app.route(variables.DEFAULT_API_URL + '/distributionpoints', methods=['POST'])
@login_required
def authenticatedRoutesGetOrPostAll():
  logs.logger.debug("Authenticated -> {}-{} ".format(request.method, request.url))
  return __getOrPostAll(current_user.is_authenticated)


@app.route(variables.DEFAULT_API_URL + '/distributionowners/<id_>', methods=['PUT'])
@app.route(variables.DEFAULT_API_URL + '/openinghourstemplates/<id_>', methods=['GET', 'PUT'])
@app.route(variables.DEFAULT_API_URL + '/recurringslotstemplates/<id_>', methods=['GET', 'PUT'])
@app.route(variables.DEFAULT_API_URL + '/addresses/<id_>', methods=['GET', 'PUT'])
@app.route(variables.DEFAULT_API_URL + '/distributionpoints/<id_>', methods=['PUT'])
@app.route(variables.DEFAULT_API_URL + '/covidtracking/<id_>', methods=['GET'])
@login_required
def authenticatedRoutesGetOrPutById(id_):
  logs.logger.debug("Authenticated -> {}-{} ".format(request.method, request.url))
  return __getOrPutOrDelById(current_user.is_authenticated, id_)
