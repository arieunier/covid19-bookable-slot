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
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/openinghourstemplates', {}, {}, {})
        self.assertEqual(code, 401)
        
        #adds an openinghourstemplate but fails because can't access it unauthenticated state
        result, code  = appsrc.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/openinghourstemplates', 
                {}, 
                {}, 
                ujson.dumps({"unknown":"param"}))
        self.assertEqual(code, 401)

    
        # access unknown data
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/openinghourstemplates/unknown', 
        {}, {}, {})
        self.assertEqual(code, 401)
        
 

    def test_access_authenticated(self):    
        # correct user/pwd
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL +'/login', {"Authorization": appsrc.tests.utils.authorizationHeader(variables.DEFAULT_ADMIN_USERNAME, variables.DEFAULT_ADMIN_PASSWORD)}, {}, {})
        session_cookie=result.headers.getlist('Set-Cookie')
        self.assertIsNotNone(session_cookie)
        self.assertEqual(code, 200)

        # gets all openinghourstemplates
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/openinghourstemplates', {'cookie':session_cookie}, {}, {})
        self.assertEqual(code, 200)
        currentNbOfAddresses = len(result.json)
        self.assertGreater(currentNbOfAddresses, 0) 

        #adds an openinghourstemplates but fails because missing name
        result, code  = appsrc.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/openinghourstemplates', 
                {'cookie':session_cookie}, 
                {}, 
                ujson.dumps({ "description":"hello", "tue":"08:00///20:00","wed":"08:00///20:00",
                "thu":"08:00///20:00", "fri":"08:00///20:00", "sat":"08:00///20:00", "sun":"08:00///20:00"
                }))
        self.assertEqual(code, 500)

        result, code  = appsrc.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/openinghourstemplates', 
                {'cookie':session_cookie}, 
                {}, 
                                ujson.dumps({'name':"test01",  "description":"hello", "mon":"///", "tue":"08:00///20:00","wed":"08:00///20:00",
                "thu":"08:00///20:00", "fri":"08:00///20:00", "sat":"08:00///20:00", "sun":"08:00///20:00"}))
        self.assertEqual(code, 200)
        print("Result=>{}".format(result))
        print("Result.json=>{}".format(result.json))
        uid = result.json['id']
        
        self.assertGreater(len(result.json), currentNbOfAddresses + 1) 

        #gets it    
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/openinghourstemplates/'+uid, 
        {'cookie':session_cookie}, {}, {})
        self.assertEqual(code, 200)
        currentNbOfAddresses = len(result.json)
        self.assertEquals(uid, result.json['id']) 

        # access unknown data
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/openinghourstemplates/unknown', 
        {'cookie':session_cookie}, {}, {})
        self.assertEqual(code, 404)
        
        #update it
        result, code  = appsrc.tests.utils.HTTP_PUT(variables.DEFAULT_API_URL + '/openinghourstemplates/'+uid, 
                {'cookie':session_cookie}, 
                {}, 
                ujson.dumps({'description':"test02"}))
        self.assertEqual(code, 200)
        self.assertEquals("test02", result.json['description'])
                
        #updates it with incorrect value
        result, code  = appsrc.tests.utils.HTTP_PUT(variables.DEFAULT_API_URL + '/openinghourstemplates/'+uid, 
                {'cookie':session_cookie}, 
                {}, 
                ujson.dumps({'name':""}))
        self.assertEqual(code, 500)
        
        
