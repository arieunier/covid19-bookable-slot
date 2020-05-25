from flask import Flask
import json
from appsrc import app, db
from libs import logs, variables

import  uuid
    
   

def fillDb():   
    from model import User, brand, company, OpeningHoursTemplate, RecurringSlotsTemplate, DailySchedule, Address, DistributionOwner, DistributionPoint, BookableSlot, BookedSlot

    db.drop_all()
    db.create_all()

    u = User(username=variables.DEFAULT_ADMIN_USERNAME,email=variables.DEFAULT_ADMIN_EMAIL,id=uuid.uuid4().__str__())
    u.set_password(variables.DEFAULT_ADMIN_PASSWORD)

    db.session.add(u)


    uid_com_1 = uuid.uuid4().__str__()
    uid_com_2 = uuid.uuid4().__str__()
    companies = [ company(id=uid_com_1,
        name='this is a first name',
        website='www.mywebsite.com'),
        company(id=uid_com_2,
        name='this is a second name',
        website='www.mywebsite2.com')]


    brands = [ brand(id=uuid.uuid4().__str__(), name='brand1', website='www.web1.com',  company_id=uid_com_1),
        brand(id=uuid.uuid4().__str__(), name='brand2', website='www.web2.com',  company_id=uid_com_1), 
        brand(id=uuid.uuid4().__str__(), name='brand3', website='www.web3.com',  company_id=uid_com_1) ]


    db.session.add_all(companies)
    db.session.commit()
    
    db.session.add_all(brands)
    db.session.commit()


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


if __name__ == "__main__":
    #purgeDb()
    #fillDb()
    #app.run()
    app.run(host='0.0.0.0', debug=False, port=int(variables.WEBPORT))