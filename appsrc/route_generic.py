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

def __insertAddresses(properClass, received_request):
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
    return newTemplate

def __insertOpeningHoursTemplate(properClass, received_request):
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
        
    db.session.add(newTemplate)
    db.session.commit()
    return newTemplate

def __insertRecurringSlotsTemplate(properClass, received_request):
    newTemplate = properClass(id = uuid.uuid4().__str__(), 
    name = received_request['name'], 
    description=received_request['description'],
    slotLength=received_request['slotLength'],
    slotCapacity=received_request['slotCapacity']
    )
    db.session.add(newTemplate)
    db.session.commit()
    return newTemplate

def __insertBookedSlots(properClass, received_request):
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
    db.session.commit()
    # updates current capacity at the bookable slot
    bookableSlot.currentCapacity -= received_request['numberOfPerson']
    flag_modified(bookableSlot, 'currentCapacity')
    db.session.commit()
    return newTemplate

def __insertCovidTracking(properClass, received_request):
    newTemplate = properClass(id = uuid.uuid4().__str__(),
        firstname = received_request['firstname'],
        lastname = received_request['lastname'],
        telephone = received_request['telephone'],
        email = received_request['email'],
        numberOfPerson = received_request['numberOfPerson'],
        refDistributionPointId = received_request['refDistributionPointId'])
    db.session.add(newTemplate)
    db.session.commit()
    return newTemplate

def __insertDistributionOwner(properClass, received_request):
    utils.checksReferencesId(properClass, received_request)      
    newTemplate = properClass(id = uuid.uuid4().__str__(),
        name = received_request['name'], 
        description=received_request['description'],
        logoUrl=received_request['logoUrl'],
        telephone=received_request['telephone'],
        email=received_request['email'],
        refAddressId=received_request['refAddressId'])    
    db.session.add(newTemplate)
    db.session.commit()
    return newTemplate

def __insertDistributionPoint(properClass, received_request):
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
    db.session.add(newTemplate)
    db.session.commit()
    return newTemplate

def __insertBookableSlot(properClass, received_request):
    newTemplate = properClass(id=uuid.uuid4().__str__(),
        dateStart = utils.getDateFromStr(received_request['dateStart'], variables.DATETIME_PATTERN),
        dateEnd = utils.getDateFromStr(received_request['dateEnd'], variables.DATETIME_PATTERN),
        maxCapacity = received_request['maxCapacity'],
        currentCapacity = received_request['currentCapacity'],
        refDistributionPointId = received_request['refDistributionPointId'])
    db.session.add(newTemplate)
    db.session.commit()
    return newTemplate

def __GET__Generic(properClass, properClassName, uri, isAdmin):
    request_filter = []
    if (properClassName == 'distributionpoints'):
        if (not 'refDistributionOwnerId' in request.args or request.args.get('refDistributionOwnerId') == '' or  request.args.get('refDistributionOwnerId') == None):
            raise Exception('Error: refDistributionOwnerId is mandatory when accessing this route')
    #checks given distribution point exist
    utils.checksReferencesId(properClass, request.args)
    #adds all params 
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
    logs.logger.info(result_dict)

    return make_response(jsonify(result_dict), 200)

def __POST__Generic(properClass, properClassName, uri, isAdmin):
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
        # currates data
        received_request = utils.currateDictValue(ujson.loads(request.json), properClass.__curratedValue__ )
        # check that there is not another objet with same information     
        utils.checkObjectUnicity(properClass, received_request)
        utils.checksReferencesId(properClass, received_request)      

        newObject = functionLoader[uri]['insert'](properClass, received_request)
        if (isAdmin):
            result_dict = newObject.serialize
        else:
            result_dict = newObject.serialize_public    
        logs.logger.info(result_dict)
        return make_response(jsonify(result_dict), 200)
    except Exception as e:
        traceback.print_exc()
        return utils.returnResponse(jsonify({'Error':e.__str__()}), 500)

def __GET_ById__Generic(properClass, properClassName, uri, isAdmin, id_):  
    noloadOptions=[]
    if (isAdmin == False): #we wont load unecessary data so we use the publicnoload attribut to avoid loading children records
        for entry in properClass.__publicNoLoadOptions__:
            noloadOptions.append(noload(entry))
    # this route has a specific behavior for bookable slots & covid tracking, so we make sure we're not in on of these context
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

    logs.logger.info(result_dict)
    return make_response(jsonify(result_dict), 200)

def __PUT_ById__Generic(properClass, properClassName, uri, isAdmin, id_):
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
    if (isAdmin):
        result_dict = objectExist.serialize
    else:
        result_dict = objectExist.serialize_public

    logs.logger.info(result_dict)
    return make_response(jsonify(result_dict), 200)

def __PUT_ById__BookedSlots(properClass, properClassName, uri, isAdmin, id_):
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

    logs.logger.info(result_dict)
    return make_response(jsonify(result_dict), 200)

def __GET_ByRefId__CovidTracking(properClass, properClassName, uri, isAdmin):
    request_filter = []
    # both covid tracking & bookable slots endpoints are using the distribution id as filter, given in the url
     # first checks the ref id given
    if ('refDistributionPointId' not in request.args):
        raise Exception('Error : refDistributionPointId is required')
    
    id_=request.args.get('refDistributionPointId')
    if (id_ == ''):
        raise Exception('Error : refDistributionPointId is required')

    utils.checksReferencesId(properClass, {"refDistributionPointId":id_})      
    request_filter.append(properClass.refDistributionPointId == id_)

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

    logs.logger.info(result_dict)
    return make_response(jsonify(result_dict), 200)

def __GET_ByRefId__BookableSlots(properClass, properClassName, uri, isAdmin):
    request_filter = []
    # both covid tracking & bookable slots endpoints are using the distribution id as filter, given in the url
    # first checks the ref id given
    if ('refDistributionPointId' not in request.args):
        raise Exception('Error : refDistributionPointId is required')
    
    id_=request.args.get('refDistributionPointId')
    if (id_ == ''):
        raise Exception('Error : refDistributionPointId is required')
    utils.checksReferencesId(properClass, {"refDistributionPointId":id_})      
    request_filter.append(properClass.refDistributionPointId == id_)


    if ('dateStart' not in request.args ):
        request_filter.append(properClass.dateStart >= utils.getCurrentDay())
    else:
        request_filter.append(properClass.dateStart >= utils.getDateFromStr(request.args.get('dateStart'), variables.DATE_PATTERN))
  
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
    logs.logger.info(result_dict)
    return make_response(jsonify(result_dict), 200)

def __DELETE_ById__BookedSlots(properClass, properClassName, uri, isAdmin, id_):
    received_request = []
    try:
        if (request.json is not None):
            received_request = ujson.loads(request.json)
    except Exception as e:
        traceback.print_exc()
    request_filter = []
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
    db.session.commit()
    result_dict=[{'Result':'Object deleted successfully'}]
    return make_response(jsonify(result_dict), 200)

def __DELETE_ById__BookableSlots(properClass, properClassName, uri, isAdmin, id_):
    bSlot = BookableSlot.query.filter_by(id=id_).first()
    if len(bSlot.bookedSlots) > 0:
        raise Exception("Can't delete this bookable slot. Some people ({}) are already registered.".format(len(bSlot.bookedSlots)))
    else:
        db.session.delete(bSlot)
    db.session.commit()
    result_dict=[{'Result':'Object deleted successfully'}]
    return make_response(jsonify(result_dict), 200)

# will be used by the functions bellow to dynamically use the proper functions
functionLoader =  {
    "/openinghourstemplates" : 
        {
            "class" : OpeningHoursTemplate, 
            "classname" : "openinghourstemplates", 
            "insert":__insertOpeningHoursTemplate,
            "GET":__GET__Generic,
            "POST": __POST__Generic
        },
    "/recurringslotstemplates" : 
        { 
            "class":  RecurringSlotsTemplate ,
            "classname" : "recurringslotstemplates", 
            "insert": __insertRecurringSlotsTemplate,
            "GET":__GET__Generic,
            "POST": __POST__Generic
        },
    "/addresses":
        {   
            "class" : Address,
            "classname" : "addresses", 
            "insert": __insertAddresses,
            "GET":__GET__Generic,
            "POST": __POST__Generic
        },
    "/distributionowners" : 
        {   
            "class" : DistributionOwner,
            "classname" : "distributionowners", 
            "insert": __insertDistributionOwner,
            "GET":__GET__Generic,
            "POST": __POST__Generic
        },
    "/distributionpoints" : 
        {   
            "class" : DistributionPoint,
            "classname" : "distributionpoints",             
            "insert": __insertDistributionPoint,
            "GET":__GET__Generic,
            "POST": __POST__Generic
        },            
    "/bookableslots" : 
        {   
            "class" : BookableSlot,
            "classname" : "bookableslots",             
            "GET": __GET_ByRefId__BookableSlots,
            "insert": __insertBookableSlot,
            "POST": __POST__Generic
        },
    "/bookedslots": 
        {   
            "class" : BookedSlot,
            "classname" : "bookedslots",             
            "insert": __insertBookedSlots,
            "GET":__GET__Generic,
            "POST": __POST__Generic
        },
    '/covidtracking':
        {   
            "class" :  CovidTracking,
            "classname" : "covidtracking",             
            "insert": __insertCovidTracking,
            "GET":__GET_ByRefId__CovidTracking,
            "POST": __POST__Generic
        },   
    '/distributionowners/<id_>': 
        {
            "class" :  DistributionOwner,
            "classname" : "distributionowners",             
            "PUT": __PUT_ById__Generic,
            "GET": __GET_ById__Generic,
        },
    '/openinghourstemplates/<id_>': 
        {
            "class" :  OpeningHoursTemplate,
            "classname" : "openinghourstemplates",             
            "PUT": __PUT_ById__Generic,
            "GET": __GET_ById__Generic,
        },
    '/recurringslotstemplates/<id_>': 
        {
            "class" :  RecurringSlotsTemplate,
            "classname" : "recurringslotstemplates",             
            "PUT": __PUT_ById__Generic,
            "GET": __GET_ById__Generic,
        },
    '/addresses/<id_>': 
        {
            "class" :  Address,
            "classname" : "addresses",             
            "PUT": __PUT_ById__Generic,
            "GET": __GET_ById__Generic,
        },
    '/distributionpoints/<id_>': 
        {
            "class" :  DistributionPoint,
            "classname" : "distributionpoints",             
            "PUT": __PUT_ById__Generic,
            "GET": __GET_ById__Generic,
        },
    '/bookableslots/<id_>': 
        {
            "class" :  BookableSlot,
            "classname" : "bookableslots",             
            "GET": __GET_ById__Generic,
            "DELETE": __DELETE_ById__BookableSlots
        },
    '/bookedslots/<id_>': 
        {
            "class" :  BookedSlot,
            "classname" : "bookedslots",             
            "PUT": __PUT_ById__BookedSlots,
            "GET": __GET_ById__Generic,
            "DELETE": __DELETE_ById__BookedSlots
        },                
    }

def genericGetPost(uri, isAdmin):
    try:
        logs.logger.debug(utils.get_debug_all(request)) 
        # check method type
        properClass = functionLoader[uri]['class']
        properClassName = functionLoader[uri]['classname']
        return functionLoader[uri][request.method](properClass, properClassName, uri, isAdmin)
        """
        if request.method == 'GET':
            if ('GET' in functionLoader[uri]):
                return functionLoader[uri]['GET'](properClass, properClassName, uri, isAdmin)
            return __GET__Generic(properClass, properClassName, uri, isAdmin)
        else:
            if ('POST' in functionLoader[uri]):
                return functionLoader[uri]['POST'](properClass, properClassName, uri, isAdmin)
            return __POST__Generic(properClass, properClassName, uri, isAdmin)
        """
    except werkzeug.exceptions.NotFound as e:
        traceback.print_exc()
        return utils.returnResponse("Requested resource does not exist", 404)        
    except Exception as e:
        traceback.print_exc()
        return utils.returnResponse("The server encountered an error while processing your request", 500)

def genericGetPutDelById(uri, isAdmin, id_):
  try:
    logs.logger.debug(utils.get_debug_all(request))
    # use the end of the route to know which class the call is meant for
    properClass = functionLoader[uri]['class']
    properClassName = functionLoader[uri]['classname']
    logs.logger.debug("properclass={}".format(properClassName))
    return functionLoader[uri][request.method](properClass, properClassName, uri, isAdmin, id_)

  except werkzeug.exceptions.NotFound as e:
    traceback.print_exc()
    return utils.returnResponse("Requested resource does not exist", 404)    
  except Exception as  e:
    traceback.print_exc()
    return utils.returnResponse("The server encountered an error while processing your request", 500)