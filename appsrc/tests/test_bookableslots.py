import os
import unittest
from appsrc import app
from libs import variables
import appsrc.tests.utils
import ujson
from datetime import datetime, timedelta
class TestCases(unittest.TestCase):
    def setUp(self):
        appsrc.tests.utils.fillDb()
        appsrc.tests.utils.purgeCookies()
        pass

    def tearDown(self):
        pass

    def test_access_unauthenticated(self):
        # gets a valid distribution point
        # authenticates properly
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/login', {"Authorization": appsrc.tests.utils.authorizationHeader(variables.DEFAULT_ADMIN_USERNAME, variables.DEFAULT_ADMIN_PASSWORD)}, {}, {})
        session_cookie=result.headers.getlist('Set-Cookie')
        self.assertIsNotNone(session_cookie)
        self.assertEqual(code, 200)
        # gets a real distribution point and saves it for later purpose
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/distributionowners', {'cookie':session_cookie}, {}, {})
        self.assertEqual(code, 200)
        distributionOwnerId = result.json[0]['id']
        # flush sessions
        appsrc.tests.utils.purgeCookies()

        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/distributionpoints', {}, {'refDistributionOwnerId':distributionOwnerId}, {})
        self.assertEqual(code, 200)
        distributionPointId = result.json[0]['id']

        # access bookable slots without a distribution poitn, must fail
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/bookableslots', {}, {}, {})
        self.assertEqual(code, 404)
    
        # access bookable slots with an incorrect dp, must fail
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/bookableslots/unknown', {}, {}, {})
        self.assertEqual(code, 500)

        # access bslots with correct dp, no date start given, will default to current
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/bookableslots/' + distributionPointId, {}, {}, {})
        self.assertEqual(code, 200)
        self.assertEqual(len(result.json), 3)

        # access bslots with correct dp, date in a day from current time
        tomorrow = (datetime.now() + timedelta(days=1)).strftime(variables.DATE_PATTERN)
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/bookableslots/' + distributionPointId, {}, {'dateStart':tomorrow}, {})
        self.assertEqual(code, 200)
        self.assertEqual(len(result.json), 1)
    
    def test_access_authenticated(self):    
        # gets all bookable slots , one will be full
        # authenticates properly
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/login', {"Authorization": appsrc.tests.utils.authorizationHeader(variables.DEFAULT_ADMIN_USERNAME, variables.DEFAULT_ADMIN_PASSWORD)}, {}, {})
        session_cookie=result.headers.getlist('Set-Cookie')
        self.assertIsNotNone(session_cookie)
        self.assertEqual(code, 200)
        # gets a real distribution point and saves it for later purpose
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/distributionowners', {'cookie':session_cookie}, {}, {})
        self.assertEqual(code, 200)
        distributionOwnerId = result.json[0]['id']
        #gets a distribution point id
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/distributionpoints', {}, {'refDistributionOwnerId':distributionOwnerId}, {})
        self.assertEqual(code, 200)
        distributionPointId = result.json[0]['id']        
        # access bslots with correct dp, no date start given, will default to current
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/bookableslots/' + distributionPointId, {}, {}, {})
        self.assertEqual(code, 200)
        self.assertEqual(len(result.json), 3)
        firstBookableSlotId = result.json[0]['id']
        secondBookableSlotId =result.json[1]['id']

        #insert a booked slot into the first bookable slot
        result, code = appsrc.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/bookedslots', {}, {},
            ujson.dumps({'refDistributionPointId': distributionPointId, "refBookableSlotId":firstBookableSlotId, 
            'firstname':'firstname', 'lastname':'lastname', 'telephone':'+1231231231', 'email':'email@me.com', 'numberOfPerson':1}))
        self.assertEqual(code, 200)
        print(result.json)
    
        #make sure capacity has decreased
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/bookableslots/' + distributionPointId, {}, {}, {})
        self.assertNotEqual(result.json[0]['maxCapacity'], result.json[0]['currentCapacity'])

        #insert a second booked slot with same info, should fail because this person already has a booked slot
        result, code = appsrc.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/bookedslots', {}, {},
            ujson.dumps({'refDistributionPointId': distributionPointId, "refBookableSlotId":firstBookableSlotId, 
            'firstname':'firstname', 'lastname':'lastname', 'telephone':'+1231231231', 'email':'email@me.com', 'numberOfPerson':1}))
        self.assertEqual(code, 500)

        #insert a second booked slot with other info, should fail because maximum capacity is reached
        result, code = appsrc.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/bookedslots', {}, {},
            ujson.dumps({'refDistributionPointId': distributionPointId, "refBookableSlotId":firstBookableSlotId, 
            'firstname':'firstname', 'lastname':'lastname', 'telephone':'+123123123213213', 'email':'email@meazeazea.com', 'numberOfPerson':3}))
        self.assertEqual(code, 500)
    
        
        # tries to delete it , shoult not work
        result, code = appsrc.tests.utils.HTTP_DEL(variables.DEFAULT_API_URL + '/bookableslots/' + firstBookableSlotId, {}, {},{})
        self.assertEqual(code, 500)
        #deletes the second properly
        result, code = appsrc.tests.utils.HTTP_DEL(variables.DEFAULT_API_URL + '/bookableslots/' + secondBookableSlotId, {}, {},{})
        self.assertEqual(code, 200)
 