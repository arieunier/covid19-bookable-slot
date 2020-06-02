import os
import unittest
from appsrc import app
from libs import variables
import appsrc.tests.utils
import ujson

class TestCases(unittest.TestCase):
    def setUp(self):
        appsrc.tests.utils.fillDb()
        appsrc.tests.utils.purgeCookies()
        pass

    def tearDown(self):
        pass

    
    def test_access_unauthenticated(self):
        # authenticates properly
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/login', {"Authorization": appsrc.tests.utils.authorizationHeader(variables.DEFAULT_ADMIN_USERNAME, variables.DEFAULT_ADMIN_PASSWORD)}, {}, {})
        session_cookie=result.headers.getlist('Set-Cookie')
        self.assertIsNotNone(session_cookie)
        self.assertEqual(code, 200)
        # gets a real distribution owner and saves it for later purpose
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/distributionowners', {'cookie':session_cookie}, {}, {})
        self.assertEqual(code, 200)
        distributionOwnerId = result.json[0]['id']
        # flush sessions
        appsrc.tests.utils.purgeCookies()
        # tries to get all distributin owner, must succeed
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/distributionowners', {}, {}, {})
        self.assertEqual(code, 200)
        
        # tries to get one distribution owner, must work
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/distributionowners/' + distributionOwnerId, {}, {}, {})
        self.assertEqual(code, 200)
        
        # tries to POST a distribution owner, must fail
        result, code  = appsrc.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/distributionowners', 
                {}, 
                {}, 
                ujson.dumps({"name":"name"}))
        self.assertEqual(code, 401)
        # tries to PUT a distribution owner, must fail
        result, code  = appsrc.tests.utils.HTTP_PUT(variables.DEFAULT_API_URL + '/distributionowners/' + distributionOwnerId, 
        {}, 
        {}, 
        ujson.dumps({"name":"enwnames"}))
        self.assertEqual(code, 401)
    

    def test_access_authenticated(self):    
        # authenticates properly
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/login', {"Authorization": appsrc.tests.utils.authorizationHeader(variables.DEFAULT_ADMIN_USERNAME, variables.DEFAULT_ADMIN_PASSWORD)}, {}, {})
        session_cookie=result.headers.getlist('Set-Cookie')
        self.assertIsNotNone(session_cookie)
        self.assertEqual(code, 200)
        # gets a real distribution owner and saves it for later purpose
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/distributionowners', {'cookie':session_cookie}, {}, {})
        self.assertEqual(code, 200)
        distributionOwnerList = result.json
        distributionOwnerId = distributionOwnerList[0]['id']
        nbDistributionOwner = len(result.json)
        # updates default DO with an incorrect value
        result, code  = appsrc.tests.utils.HTTP_PUT(variables.DEFAULT_API_URL + '/distributionowners/' + distributionOwnerId, 
                    {'cookie':session_cookie}, 
                    {}, 
                     ujson.dumps({"name":""}))
        self.assertEqual(code, 500)
        print(result.json)
        # updates default DO with a correct value
        result, code  = appsrc.tests.utils.HTTP_PUT(variables.DEFAULT_API_URL + '/distributionowners/' + distributionOwnerId, 
                    {'cookie':session_cookie}, 
                    {}, 
                     ujson.dumps({"name":"ANewValue"}))
        self.assertEqual(code, 200)
        self.assertEqual(result.json['name'], 'ANewValue')        

        # creates a new DO -> wrong value & no references filled 
        result, code =  appsrc.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/distributionowners', 
                    {'cookie':session_cookie}, 
                    {}, 
                     ujson.dumps({"name":""}))        
        self.assertEqual(code, 500)                             
        # check it has NOT BEEN ADDED
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/distributionowners', {'cookie':session_cookie}, {}, {})        
        self.assertEqual(len(result.json), nbDistributionOwner)

        result, code =  appsrc.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/distributionowners', 
                    {'cookie':session_cookie}, 
                    {}, 
                     ujson.dumps({"name":"correct", "logoUrl":""}))
        self.assertEqual(code, 500)       
        # check it has NOT BEEN ADDED
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/distributionowners', {'cookie':session_cookie}, {}, {})
        self.assertEqual(len(result.json), nbDistributionOwner)

        result, code =  appsrc.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/distributionowners', 
                    {'cookie':session_cookie}, 
                    {}, 
                     ujson.dumps({"name":"correct", "logoUrl":"www.google.fr", "telephone":""}))
        self.assertEqual(code, 500)   
        # check it has NOT BEEN ADDED
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/distributionowners', {'cookie':session_cookie}, {}, {})
        self.assertEqual(len(result.json), nbDistributionOwner)

        result, code =  appsrc.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/distributionowners', 
                    {'cookie':session_cookie}, 
                    {}, 
                     ujson.dumps({"name":"correct", "logoUrl":"www.google.fr", "telephone":"01232132131", "email":""}))
        self.assertEqual(code, 500)    
        # check it has NOT BEEN ADDED
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/distributionowners', {'cookie':session_cookie}, {}, {})
        self.assertEqual(len(result.json), nbDistributionOwner)

        # creates a new DO -> correct values & no reference address
        result, code =  appsrc.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/distributionowners', 
                    {'cookie':session_cookie}, 
                    {}, 
                     ujson.dumps({"name":"correct", "logoUrl":"www.google.fr", "telephone":"01232132131", "email":"test@test.com", "refAddressId":""}))
        self.assertEqual(code, 500)                               
        # check it has NOT BEEN ADDED
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/distributionowners', {'cookie':session_cookie}, {}, {})
        self.assertEqual(len(result.json), nbDistributionOwner)

        result, code =  appsrc.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/distributionowners', 
                    {'cookie':session_cookie}, 
                    {}, 
                     ujson.dumps({"name":"correct", "logoUrl":"www.google.fr", "telephone":"01232132131", "email":"test@test.com", "refAddressId":"unknown"}))
        self.assertEqual(code, 500)                                                    
        # check it has NOT BEEN ADDED
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/distributionowners', {'cookie':session_cookie}, {}, {})
        self.assertEqual(len(result.json), nbDistributionOwner)


        # creates a new DO -> unicity check on phone numner
        result, code =  appsrc.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/distributionowners', 
                    {'cookie':session_cookie}, 
                    {}, 
                     ujson.dumps({"name":"correct", "logoUrl":"www.google.fr", "telephone":distributionOwnerList[0]['telephone'], "email":"test@test.com", "refAddressId":distributionOwnerList[0]['address']['id']}))                     
        self.assertEqual(code, 500)                                       

        # creates a new DO -> unicity check on email
        result, code =  appsrc.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/distributionowners', 
                    {'cookie':session_cookie}, 
                    {}, 
                     ujson.dumps({"name":"correct", "logoUrl":"www.google.fr", "telephone":"01232132131", "email":distributionOwnerList[0]['email'], "refAddressId":distributionOwnerList[0]['address']['id']}))                     
        self.assertEqual(code, 500)  

        result, code =  appsrc.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/distributionowners', 
                    {'cookie':session_cookie}, 
                    {}, 
                     ujson.dumps({"name":"correct", "logoUrl":"www.google.fr", "telephone":"01232132131", "email":"test@test.com", "refAddressId":distributionOwnerList[0]['address']['id']}))                     
        self.assertEqual(code, 200)        
        newDO =  result.json['id']
        # check list of DO 
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/distributionowners', {'cookie':session_cookie}, {}, {})
        self.assertEqual(len(result.json), nbDistributionOwner + 1)
        
        # update duplicate on email
        result, code =  appsrc.tests.utils.HTTP_PUT(variables.DEFAULT_API_URL + '/distributionowners/' +newDO , 
                    {'cookie':session_cookie}, 
                    {}, 
                     ujson.dumps({"email":distributionOwnerList[0]['email']}))                     
        self.assertEqual(code, 500)   
        # duplicate on telephone
        result, code =  appsrc.tests.utils.HTTP_PUT(variables.DEFAULT_API_URL + '/distributionowners/' +newDO , 
                    {'cookie':session_cookie}, 
                    {}, 
                     ujson.dumps({"telephone":distributionOwnerList[0]['telephone']})) 
        self.assertEqual(code, 500)   
        

        pass
        
