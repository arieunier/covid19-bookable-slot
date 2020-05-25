from appsrc import app
from appsrc import db
import unittest
import variables 
import uuid 

from appsrc.tests import utils, test_login, test_addresses, test_openinghourstemplates




TEST_DB = 'test.db'
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False
app.config['DEBUG'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'


appclient = app.test_client()


def suite():
    suite = unittest.TestSuite()
    
    suite.addTest(unittest.makeSuite(test_login.TestCases))
    #suite.addTest(unittest.makeSuite(test_opein.TestCases))
    return suite
 

def fillDb():   
    print("Creating DB")
    from model import User, OpeningHoursTemplate, RecurringSlotsTemplate, DailySchedule, Address, DistributionOwner, DistributionPoint, BookableSlot, BookedSlot

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

if __name__ == '__main__':
    fillDb()
    print("now calling tests")
    unittest.main(warnings='ignore',verbosity=0,defaultTest='suite')
    print("ending tests")