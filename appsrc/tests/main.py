from appsrc import app
from appsrc import db
import unittest
from libs import variables
import uuid 

from appsrc.tests import utils, test_login, test_addresses, test_openinghourstemplates, test_distributionowners, test_recurringslotstemplates, test_distributionpoints, test_bookableslots, test_bookedslots, test_covidtracking




TEST_DB = 'test.db'
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False
app.config['DEBUG'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'


appclient = app.test_client()


def suite():
    suite = unittest.TestSuite()
    
    #DONE
    
    #suite.addTest(unittest.makeSuite(test_addresses.TestCases))
    suite.addTest(unittest.makeSuite(test_distributionowners.TestCases))    

    #suite.addTest(unittest.makeSuite(test_openinghourstemplates.TestCases))    
    #suite.addTest(unittest.makeSuite(test_recurringslotstemplates.TestCases))
    
    #suite.addTest(unittest.makeSuite(test_distributionpoints.TestCases))
    #suite.addTest(unittest.makeSuite(test_covidtracking.TestCases))
    #suite.addTest(unittest.makeSuite(test_login.TestCases))
    #suite.addTest(unittest.makeSuite(test_bookableslots.TestCases))
    #suite.addTest(unittest.makeSuite(test_bookedslots.TestCases))
    #
    #TODO
    
    
    # distribution points
    # bookedslotss
    # covidtracking
    return suite
 

if __name__ == '__main__':
    print("now calling tests")
    unittest.main(warnings='ignore',verbosity=0,defaultTest='suite')
    print("ending tests")