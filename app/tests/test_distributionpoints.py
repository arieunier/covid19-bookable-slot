import os
import unittest
from app import app
from libs import variables
import app.tests.utils
import ujson

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
        # flush sessions
        app.tests.utils.purgeCookies()

        result, code = app.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/distributionpoints', {}, {'refDistributionOwnerId':distributionOwnerId}, {})
        self.assertEqual(code, 200)
        distributionPointId = result.json[0]['id']

        # tries to get all distributin owner, must fail because the distribution owner id must be given
        result, code = app.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/distributionpoints', {}, {}, {})
        self.assertEqual(code, 500)

        # gets all Distrbution point but with a wrong DO
        result, code = app.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/distributionpoints', {}, {'refDistributionOwnerId':'idontexist'}, {})
        self.assertEqual(code, 500)
        
        # tries to get one distribution point, must work
        result, code = app.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/distributionpoints/' + distributionPointId, {}, {}, {})
        self.assertEqual(code, 200)
        
        # tries to POST a distribution owner, must fail
        result, code  = app.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/distributionpoints', 
                {}, 
                {}, 
                ujson.dumps({"name":"name"}))
        self.assertEqual(code, 401)
        # tries to PUT a distribution owner, must fail
        result, code  = app.tests.utils.HTTP_PUT(variables.DEFAULT_API_URL + '/distributionpoints/' + distributionOwnerId, 
        {}, 
        {}, 
        ujson.dumps({"name":"enwnames"}))
        self.assertEqual(code, 401)

    

    def test_access_authenticated(self):    
        # authenticates properly
        result, code = app.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/login', {"Authorization": app.tests.utils.authorizationHeader(variables.DEFAULT_ADMIN_USERNAME, variables.DEFAULT_ADMIN_PASSWORD)}, {}, {})
        session_cookie=result.headers.getlist('Set-Cookie')
        self.assertIsNotNone(session_cookie)
        self.assertEqual(code, 200)
        # gets a real distribution owner and saves it for later purpose
        result, code = app.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/distributionowners', {'cookie':session_cookie}, {}, {})
        self.assertEqual(code, 200)
        distributionOwnerList = result.json
        distributionOwnerId = distributionOwnerList[0]['id']
        distributionPointId = distributionOwnerList[0]['distributionPoints'][0]['id']
        nbDistributionPoint = len(distributionOwnerList[0]['distributionPoints'])
        refAddressId = distributionOwnerList[0]['address']['id']
        # gets a real openinghourstemplate
        result, code = app.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/openinghourstemplates', {'cookie':session_cookie}, {}, {})
        self.assertEqual(code, 200)
        refOpeningHoursTemplateId=result.json[0]['id']
        # gets a real recurringslottemplate
        result, code = app.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/recurringslotstemplates', {'cookie':session_cookie}, {}, {})
        self.assertEqual(code, 200)
        refRecurringSlotsTemplate=result.json[0]['id']

        
        # updates default DP with an incorrect values
        result, code  = app.tests.utils.HTTP_PUT(variables.DEFAULT_API_URL + '/distributionpoints/' + distributionPointId, 
                    {'cookie':session_cookie}, 
                    {}, 
                     ujson.dumps({"name":""}))
        self.assertEqual(code, 500)
        # updates default DP with a correct value
        result, code  = app.tests.utils.HTTP_PUT(variables.DEFAULT_API_URL + '/distributionpoints/' + distributionPointId, 
                    {'cookie':session_cookie}, 
                    {}, 
                     ujson.dumps({"name":"ANewValue"}))
        self.assertEqual(code, 200)
        # gets  it and check that  it's been update properly
        result, code  = app.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/distributionpoints/' + distributionPointId, 
                    {'cookie':session_cookie}, 
                    {}, 
                     {})
        self.assertEqual(result.json['name'], 'ANewValue')        

        

        # creates a new DP -> wrong value & no references filled 
        result, code =  app.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/distributionpoints', 
                    {'cookie':session_cookie}, 
                    {}, 
                     ujson.dumps({"name":""}))        
        self.assertEqual(code, 500)                             
        # check it has NOT BEEN ADDED
        result, code = app.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/distributionpoints' , {'cookie':session_cookie},  {'refDistributionOwnerId':distributionOwnerId}, {})        
        self.assertEqual(len(result.json), nbDistributionPoint)

        # gives everything BUT references
        result, code =  app.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/distributionpoints', 
                    {'cookie':session_cookie}, 
                    {}, 
                     ujson.dumps({"name":"correct", "logoUrl": "wwW.google.Fr", "telephone":"123", "email":"mail@mail.com", "maxCapacity":10}))        
        self.assertEqual(code, 500)                             
        # check it has NOT BEEN ADDED
        result, code = app.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/distributionpoints' , {'cookie':session_cookie},  {'refDistributionOwnerId':distributionOwnerId}, {})        
        self.assertEqual(len(result.json), nbDistributionPoint)


        # gives everything BUT references
        result, code =  app.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/distributionpoints', 
                    {'cookie':session_cookie}, 
                    {}, 
                     ujson.dumps({"name":"correct", "logoUrl": "wwW.google.Fr", "telephone":"123", "email":"mail@mail.com", "maxCapacity":10}))        
        self.assertEqual(code, 500)                             
        # check it has NOT BEEN ADDED
        result, code = app.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/distributionpoints' , {'cookie':session_cookie},  {'refDistributionOwnerId':distributionOwnerId}, {})        
        self.assertEqual(len(result.json), nbDistributionPoint)

        
        
        # adds all references
        result, code =  app.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/distributionpoints', 
                    {'cookie':session_cookie}, 
                    {}, 
                     ujson.dumps({"name":"correct", "logoUrl": "wwW.google.Fr", "telephone":"123", "email":"mail@mail.com", "maxCapacity":10, 'refAddressId' : refAddressId, 'refDistributionOwnerId':distributionOwnerId,
                     'refOpeningHoursTemplateId':refOpeningHoursTemplateId, 'refRecurringSlotsTemplateId':refRecurringSlotsTemplate }))        
        newDPID = result.json['id']                          
        self.assertEqual(code, 200)                             
        # check it has  BEEN ADDED
        result, code = app.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/distributionpoints' , {'cookie':session_cookie},  {'refDistributionOwnerId':distributionOwnerId}, {})   

        self.assertEqual(code, 200)                             
        self.assertEqual(len(result.json), nbDistributionPoint + 1)


        # unicity checks on create, unicity is on email / telephone
        result, code =  app.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/distributionpoints', 
                    {'cookie':session_cookie}, 
                    {}, 
                     ujson.dumps({"name":"correct", "logoUrl": "wwW.google.Fr", "telephone":distributionOwnerList[0]['distributionPoints'][0]['telephone'], 
                     "email":"mail@mail.com", "maxCapacity":10, 'refAddressId' : refAddressId, 'refDistributionOwnerId':distributionOwnerId,
                     'refOpeningHoursTemplateId':refOpeningHoursTemplateId, 'refRecurringSlotsTemplateId':refRecurringSlotsTemplate }))        
        self.assertEqual(code, 500)     
        result, code =  app.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/distributionpoints', 
                    {'cookie':session_cookie}, 
                    {}, 
                     ujson.dumps({"name":"correct", "logoUrl": "wwW.google.Fr", "telephone":"12312312", 
                     "email":distributionOwnerList[0]['distributionPoints'][0]['email'], "maxCapacity":10, 'refAddressId' : refAddressId, 'refDistributionOwnerId':distributionOwnerId,
                     'refOpeningHoursTemplateId':refOpeningHoursTemplateId, 'refRecurringSlotsTemplateId':refRecurringSlotsTemplate }))        
        self.assertEqual(code, 500)     

        # unicity checks on update
        result, code =  app.tests.utils.HTTP_PUT(variables.DEFAULT_API_URL + '/distributionpoints/' +newDPID, 
                    {'cookie':session_cookie}, 
                    {}, 
                     ujson.dumps({"email":distributionOwnerList[0]['distributionPoints'][0]['email']}))        
        self.assertEqual(code, 500)   
        result, code =  app.tests.utils.HTTP_PUT(variables.DEFAULT_API_URL + '/distributionpoints/' +newDPID, 
                    {'cookie':session_cookie}, 
                    {}, 
                     ujson.dumps({"telephone":distributionOwnerList[0]['distributionPoints'][0]['telephone']}))        
        self.assertEqual(code, 500)           

        pass
        
        