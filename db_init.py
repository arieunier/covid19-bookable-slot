from appsrc import app, db
from appsrc.model import User
from libs import logs, variables
import uuid
from datetime import datetime, timedelta

if (len(db.session.query(User).all()) == 0):
    from appsrc.model import User, OpeningHoursTemplate, RecurringSlotsTemplate, DailySchedule, Address, DistributionOwner, DistributionPoint, BookableSlot, BookedSlot

    logs.logger.info("Dropping DB")
    db.session.remove()
    db.session.commit()  
    db.drop_all()
    logs.logger.info("Creating a new version of the db")
    db.create_all()
    logs.logger.info("Adding User")
    u = User(username=variables.DEFAULT_ADMIN_USERNAME,email=variables.DEFAULT_ADMIN_EMAIL,id=uuid.uuid4().__str__())
    u.set_password(variables.DEFAULT_ADMIN_PASSWORD)
    db.session.add(u)


    #openinghourstemplate
    sched = DailySchedule("09:00", "", "", "19:00")
    sched_str = sched.serialize.__str__()
    openHTemplateId = uuid.uuid4().__str__()
    openHTemplate = OpeningHoursTemplate(id=openHTemplateId, name="24/7", description="Open 24/7",mon=sched_str, tue=sched_str, wed=sched_str, thu=sched_str, fri=sched_str,
    sat=sched_str, sun=sched_str,)
    db.session.add(openHTemplate)
    db.session.commit()
    logs.logger.info("Adding RST")
    #recurringSlotsTemplateId
    recurringSlotsTemplateId = uuid.uuid4().__str__()
    recurringSlotsTemplate = RecurringSlotsTemplate(id=recurringSlotsTemplateId, name="Default template", description="default slot, 30 min slot length",
    slotLength=30, slotCapacity=10)
    db.session.add(recurringSlotsTemplate)
    db.session.commit()


    """    
    logs.logger.info("Adding address")
    # ADDRESS PART
    add_uid = uuid.uuid4().__str__()
    add = Address(id=add_uid, street='Rue Mertens', number="2", zipcode="92270", city="Bois Colombes", country="France")
    db.session.add(add)
    db.session.commit()
    logs.logger.info("Adding OHT")


    logs.logger.info("Adding DO")
    # DistributionOwner Part
    owner_id = uuid.uuid4().__str__()
    distO = DistributionOwner(id=owner_id, name="my name", description="my description", logoUrl="https://www.www.col", telephone="01203013123", email="koko@koko.com")
    distO.refAddressId = add.id
    db.session.add(distO)
    db.session.commit()
    logs.logger.info("Adding DP")
    #DistributionPoint Part
    distPart = uuid.uuid4().__str__()
    dP0 = DistributionPoint(id=distPart, name="my name", description="my description", logoUrl="https://www.www.col", telephone="01203013123", email="koko@koko.com",
        refAddressId = add.id,  refDistributionOwnerId=owner_id, maxCapacity=10, refOpeningHoursTemplateId=openHTemplateId, refRecurringSlotsTemplateId=recurringSlotsTemplateId)
    db.session.add(dP0)
    db.session.commit()
    logs.logger.info("Adding BS")
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
    """