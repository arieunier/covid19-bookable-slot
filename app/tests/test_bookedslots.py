import os
import unittest
from app import app
from libs import variables
import app.tests.utils
import ujson
from datetime import datetime, timedelta
class TestCases(unittest.TestCase):
    def setUp(self):
        app.tests.utils.fillDb()
        app.tests.utils.purgeCookies()
        pass

    def tearDown(self):
        pass

    def test_access_unauthenticated(self):
        # authenticates properly
        result, code = app.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/login', {"Authorization": app.tests.utils.authorizationHeader(variables.DEFAULT_ADMIN_USERNAME, variables.DEFAULT_ADMIN_PASSWORD)}, {}, {})
        session_cookie=result.headers.getlist('Set-Cookie')
        self.assertIsNotNone(session_cookie)
        self.assertEqual(code, 200)
        # gets a real distribution point and saves it for later purpose
        result, code = app.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/distributionowners', {'cookie':session_cookie}, {}, {})
        self.assertEqual(code, 200)
        distributionOwnerId = result.json[0]['id']
        #gets a distribution point id
        result, code = app.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/distributionpoints', {}, {'refDistributionOwnerId':distributionOwnerId}, {})
        self.assertEqual(code, 200)
        distributionPointId = result.json[0]['id']        
        # access bslots with correct dp, no date start given, will default to current
        result, code = app.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/bookableslots/' + distributionPointId, {}, {}, {})
        self.assertEqual(code, 200)
        self.assertEqual(len(result.json), 3)
        firstBookableSlotId = result.json[0]['id']
        secondBookableSlotId =result.json[1]['id']
        thirdBookableSlot =result.json[2]['id']
        # flush sessions
        app.tests.utils.purgeCookies()

        #insert a booked slot into the first bookable slot
        result, code = app.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/bookedslots', {}, {},
            ujson.dumps({'refDistributionPointId': distributionPointId, "refBookableSlotId":firstBookableSlotId, 
            'firstname':'firstname', 'lastname':'lastname', 'telephone':'+1231231231', 'email':'email@me.com', 'numberOfPerson':1}))
        self.assertEqual(code, 200)
        print(result.json)
        bookedSlotId = result.json['id']
        bookedSlotCode = result.json['confirmationCode']
        
        # insert it on the second, must fail
        result, code = app.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/bookedslots', {}, {},
            ujson.dumps({'refDistributionPointId': distributionPointId, "refBookableSlotId":secondBookableSlotId, 
            'firstname':'firstname', 'lastname':'lastname', 'telephone':'+1231231231', 'email':'email@me.com', 'numberOfPerson':1}))
        self.assertEqual(code, 500)

        # tries to get the booking without the code, must fail
        result, code = app.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/bookedslots/' + bookedSlotId, {}, {}, {})
        self.assertEqual(code, 500)
        # tries to get the booking with the code, must work
        result, code = app.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/bookedslots/' + bookedSlotId, {}, {}, ujson.dumps({'confirmationCode':bookedSlotCode}))
        self.assertEqual(code, 200) 
        
        
        # updates the booking without the code, must fail
        result, code = app.tests.utils.HTTP_PUT(variables.DEFAULT_API_URL + '/bookedslots/' + bookedSlotId, {}, {}, ujson.dumps({'firstname':'newfname', }))
        self.assertEqual(code, 500)

        # updates the booking without  code but with wrong data, must fail
        result, code = app.tests.utils.HTTP_PUT(variables.DEFAULT_API_URL + '/bookedslots/' + bookedSlotId, {}, {}, ujson.dumps({'firstname':'', 'confirmationCode':bookedSlotCode}))
        self.assertEqual(code, 500)

        # updates the booking without  code but with correct data, must work
        result, code = app.tests.utils.HTTP_PUT(variables.DEFAULT_API_URL + '/bookedslots/' + bookedSlotId, {}, {}, ujson.dumps({'firstname':'new name', 'confirmationCode':bookedSlotCode}))
        self.assertEqual(code, 200)

        # updating nb of person  but more capacity
        result, code = app.tests.utils.HTTP_PUT(variables.DEFAULT_API_URL + '/bookedslots/' + bookedSlotId, {}, {}, ujson.dumps({'numberOfPerson':3, 'confirmationCode':bookedSlotCode}))
        self.assertEqual(code, 500)

        # updating nb of person  but correct capacity
        result, code = app.tests.utils.HTTP_PUT(variables.DEFAULT_API_URL + '/bookedslots/' + bookedSlotId, {}, {}, ujson.dumps({'numberOfPerson':2, 'confirmationCode':bookedSlotCode}))
        self.assertEqual(code, 200)
        #make sure capacity has decreased
        result, code = app.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/bookableslots/' + distributionPointId, {}, {}, {})
        self.assertEqual(0, result.json[0]['currentCapacity'])


        # changes to another ref, forbidden
        result, code = app.tests.utils.HTTP_PUT(variables.DEFAULT_API_URL + '/bookedslots/' + bookedSlotId, {}, {}, ujson.dumps({'refBookableSlotId':secondBookableSlotId, 'confirmationCode':bookedSlotCode}))
        self.assertEqual(code, 500)


        #make sure capacity has decreased
        result, code = app.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/bookableslots/' + distributionPointId, {}, {}, {})
        self.assertNotEqual(result.json[0]['maxCapacity'], result.json[0]['currentCapacity'])

        #insert a second booked slot with same info, should fail because this person already has a booked slot
        result, code = app.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/bookedslots', {}, {},
            ujson.dumps({'refDistributionPointId': distributionPointId, "refBookableSlotId":firstBookableSlotId, 
            'firstname':'firstname', 'lastname':'lastname', 'telephone':'+1231231231', 'email':'email@me.com', 'numberOfPerson':1}))
        self.assertEqual(code, 500)

        #insert a second booked slot with other info, should fail because maximum capacity is reached
        result, code = app.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/bookedslots', {}, {},
            ujson.dumps({'refDistributionPointId': distributionPointId, "refBookableSlotId":firstBookableSlotId, 
            'firstname':'firstname', 'lastname':'lastname', 'telephone':'+123123123213213', 'email':'email@meazeazea.com', 'numberOfPerson':1}))
        self.assertEqual(code, 500)

        
        # deletes the slot
        result, code = app.tests.utils.HTTP_DEL(variables.DEFAULT_API_URL + '/bookedslots/' + bookedSlotId, {}, {}, ujson.dumps({'confirmationCode':bookedSlotCode}))
        self.assertEqual(code, 200)

        #check slot capacity
        result, code = app.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/bookableslots/' + distributionPointId, {}, {}, {})                
        self.assertEqual(2, result.json[0]['currentCapacity'])

    

 