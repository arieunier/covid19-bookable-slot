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
        
        # gets all addresses
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/addresses', {}, {}, {})
        self.assertEqual(code, 401)
        
        #adds an adress but fails because can't access it unauthenticated state
        result, code  = appsrc.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/addresses', 
                {}, 
                {}, 
                ujson.dumps({'street':"test01", "number":"1", "zipcode":'12345', "city":'Paris', "country":"France"}))
        self.assertEqual(code, 401)

    
        # access unknown data
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/addresses/unknown', 
        {}, {}, {})
        self.assertEqual(code, 401)
        
 

    def test_access_authenticated(self):    
        # correct user/pwd
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/login', {"Authorization": appsrc.tests.utils.authorizationHeader(variables.DEFAULT_ADMIN_USERNAME, variables.DEFAULT_ADMIN_PASSWORD)}, {}, {})
        session_cookie=result.headers.getlist('Set-Cookie')
        self.assertIsNotNone(session_cookie)
        self.assertEqual(code, 200)

        # gets all addresses
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/addresses', {'cookie':session_cookie}, {}, {})
        self.assertEqual(code, 200)
        currentNbOfAddresses = len(result.json)
        self.assertGreater(currentNbOfAddresses, 0) 

        #adds an adress but fails because missing state
        result, code  = appsrc.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/addresses', 
                {'cookie':session_cookie}, 
                {}, 
                ujson.dumps({'street':"test01", "number":"1", "zipcode":'12345', "city":'Paris', "country":"France"}))
        self.assertEqual(code, 500)

        result, code  = appsrc.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/addresses', 
                {'cookie':session_cookie}, 
                {}, 
                ujson.dumps({'street':"test01", "number":"1", "zipcode":'12345', "city":'Paris', "country":"France", "state":"paris"}))
        self.assertEqual(code, 200)
        print("Result=>{}".format(result))
        print("Result.json=>{}".format(result.json))
        address_id = result.json['id']
        
        self.assertGreater(len(result.json), currentNbOfAddresses + 1) 

        #gets it    
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/addresses/'+address_id, 
        {'cookie':session_cookie}, {}, {})
        self.assertEqual(code, 200)
        currentNbOfAddresses = len(result.json)
        self.assertEquals(address_id, result.json['id']) 

        # access unknown data
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/addresses/unknown', 
        {'cookie':session_cookie}, {}, {})
        self.assertEqual(code, 404)
        
        #update it
        result, code  = appsrc.tests.utils.HTTP_PUT(variables.DEFAULT_API_URL + '/addresses/'+address_id, 
                {'cookie':session_cookie}, 
                {}, 
                ujson.dumps({'street':"test02"}))
        self.assertEqual(code, 200)
        self.assertEquals("test02", result.json['street'])
                
        #updates it with incorrect value
        result, code  = appsrc.tests.utils.HTTP_PUT(variables.DEFAULT_API_URL + '/addresses/'+address_id, 
                {'cookie':session_cookie}, 
                {}, 
                ujson.dumps({'street':""}))
        self.assertEqual(code, 500)
        
        
