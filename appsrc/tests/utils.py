from appsrc.tests.main import appclient
import traceback
from libs import variables
import base64
import uuid
from appsrc import db
from datetime import datetime, timedelta


def fillDb():
    print("Creating DB")
    from appsrc.model import User, OpeningHoursTemplate, RecurringSlotsTemplate, DailySchedule, Address, DistributionOwner, DistributionPoint, BookableSlot, BookedSlot

    db.drop_all()
    db.create_all()

    u = User(username=variables.DEFAULT_ADMIN_USERNAME,email=variables.DEFAULT_ADMIN_EMAIL,id=uuid.uuid4().__str__())
    u.set_password(variables.DEFAULT_ADMIN_PASSWORD)

    db.session.add(u)

    # ADDRESS PART
    add_uid = uuid.uuid4().__str__()
    add = Address(id=add_uid, street='Rue Mertens', number="2", zipcode="92270", city="Bois Colombes", country="France")
    db.session.add(add)
    db.session.commit()

    #openinghourstemplate
    sched = DailySchedule("09:00", "", "", "19:00")
    sched_str = sched.serialize.__str__()
    openHTemplateId = uuid.uuid4().__str__()
    openHTemplate = OpeningHoursTemplate(id=openHTemplateId, name="24/7", description="Open 24/7",mon=sched_str, tue=sched_str, wed=sched_str, thu=sched_str, fri=sched_str,
    sat=sched_str, sun=sched_str,)
    db.session.add(openHTemplate)
    db.session.commit()

    #recurringSlotsTemplateId
    recurringSlotsTemplateId = uuid.uuid4().__str__()
    recurringSlotsTemplate = RecurringSlotsTemplate(id=recurringSlotsTemplateId, name="Default template", description="default slot, 30 min slot length",
    slotLength=30, slotCapacity=10)
    db.session.add(recurringSlotsTemplate)
    db.session.commit()


    # DistributionOwner Part
    owner_id = uuid.uuid4().__str__()
    distO = DistributionOwner(id=owner_id, name="my name", description="my description", logoUrl="https://www.www.col", telephone="01203013123", email="koko@koko.com")
    distO.refAddressId = add.id
    db.session.add(distO)
    db.session.commit()

    #DistributionPoint Part
    distPart = uuid.uuid4().__str__()
    dP0 = DistributionPoint(id=distPart, name="my name", description="my description", logoUrl="https://www.www.col", telephone="01203013123", email="koko@koko.com",
        refAddressId = add.id,  refDistributionOwnerId=owner_id, maxCapacity=10, refOpeningHoursTemplateId=openHTemplateId, refRecurringSlotsTemplateId=recurringSlotsTemplateId)
    db.session.add(dP0)
    db.session.commit()

    # adds a bookable slot
    BS1Id = uuid.uuid4().__str__()
    now = datetime.now()
    BS = BookableSlot(id=BS1Id, dateStart=now - timedelta(minutes=1), dateEnd=now + timedelta(minutes=40), maxCapacity=2, refDistributionPointId=distPart, currentCapacity=2)
    db.session.add(BS)
    db.session.commit()

    BS11Id = uuid.uuid4().__str__()
    BS11 = BookableSlot(id=BS11Id, dateStart=now + timedelta(hours=1), dateEnd=now + timedelta(hours=2), maxCapacity=10, refDistributionPointId=distPart, currentCapacity=10)
    db.session.add(BS11)
    db.session.commit()


    BS2Id = uuid.uuid4().__str__()
    BS2 = BookableSlot(id=BS2Id, dateStart=now + timedelta(hours=23), dateEnd=now + timedelta(hours=25), maxCapacity=10, refDistributionPointId=distPart, currentCapacity=0)
    db.session.add(BS2)
    db.session.commit()

def purgeCookies():
    appclient.cookie_jar.clear()
    appclient.cookie_jar.clear_session_cookies()
    
def authorizationHeader(username, password):
    toEncode = username + ":" + password
    message_bytes = toEncode.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    #b64version = base64.b64encode(toEncode.encode('utf-8')    
    return "Basic " + base64_bytes.decode('utf-8')
          
    
def HTTP_GET(uri, headers, params, data):
    try:
        result = appclient.get(uri,
            headers=headers,
            query_string = params, json=data )
        return result, result.status_code
    except Exception as e:
        traceback.print_exc()
        return "Error", 500

def HTTP_PUT(uri, headers, params, data):
    try:
        result = appclient.put(uri,
            headers=headers,
            query_string = params, json=data)
        return result, result.status_code
    except Exception as e:
        traceback.print_exc()
        return "Error", 500

def HTTP_POST(uri, headers, params, data):
    try:
        result = appclient.post(uri,
            headers=headers,
            query_string = params, json=data)

        return result, result.status_code
    except Exception as e:
        traceback.print_exc()
        return "Error", 500

def HTTP_DEL(uri, headers, params, data):
    try:
        result = appclient.delete(uri,
            headers=headers,
            query_string = params, json=data)

        return result, result.status_code
    except Exception as e:
        traceback.print_exc()
        return "Error", 500

def getDayFromStr(date):
    today = datetime.strptime((datetime.now()).strftime(variables.DATE_PATTERN), variables.DATE_PATTERN)
    return today

def getCurrentDay():
    today = datetime.strptime((datetime.now()).strftime(variables.DATE_PATTERN), variables.DATE_PATTERN)
    return today

def getTomorrowDT():
    tomorrow = datetime.strptime((datetime.now() + timedelta(days=1)).strftime(variables.DATE_PATTERN), variables.DATE_PATTERN)
    return tomorrow

def getDateFromStr(str, pattern):
    return datetime.strptime(str, pattern)

def dateToStr(date, pattern):
    return date.strftime(pattern)