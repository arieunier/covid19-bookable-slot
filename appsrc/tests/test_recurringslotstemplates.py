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
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/recurringslotstemplates', {'cookie':session_cookie}, {}, {})
        self.assertEqual(code, 200)
        recSlotId = result.json[0]['id']
        # flush sessions
        appsrc.tests.utils.purgeCookies()
        # gets all recurringslottemplates
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/recurringslotstemplates', {}, {}, {})
        self.assertEqual(code, 401)
        # gets A recurringslottemplate
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/recurringslotstemplates/' + recSlotId, {}, {}, {})
        self.assertEqual(code, 401)
        # tries to update the correct recurring slot template
        result, code = appsrc.tests.utils.HTTP_PUT(variables.DEFAULT_API_URL + '/recurringslotstemplates/' + recSlotId, {}, {}, {'name':'unknown'})
        self.assertEqual(code, 401)

        #adds an openinghourstemplate but fails because can't access it unauthenticated state
        result, code  = appsrc.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/recurringslotstemplates', 
                {}, 
                {}, 
                ujson.dumps({"unknown":"param"}))
        self.assertEqual(code, 401)
 
        # access unknown data
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/recurringslotstemplates/unknown', 
        {}, {}, {})
        self.assertEqual(code, 401)
        
    
    def test_access_authenticated(self):    
        # correct user/pwd
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL +'/login', {"Authorization": appsrc.tests.utils.authorizationHeader(variables.DEFAULT_ADMIN_USERNAME, variables.DEFAULT_ADMIN_PASSWORD)}, {}, {})
        session_cookie=result.headers.getlist('Set-Cookie')
        self.assertIsNotNone(session_cookie)
        self.assertEqual(code, 200)

        # gets all openinghourstemplates
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/recurringslotstemplates', {'cookie':session_cookie}, {}, {})
        self.assertEqual(code, 200)
        nbRecurringSlotTemplates = len(result.json)
        self.assertGreater(nbRecurringSlotTemplates, 0) 


        #adds an openinghourstemplates but fails because missing name
        result, code  = appsrc.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/recurringslotstemplates', 
                {'cookie':session_cookie}, 
                {}, 
                ujson.dumps({ 'description':'unknown description'}))
        self.assertEqual(code, 500)
        # name  is here,  but no lenght
        result, code  = appsrc.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/recurringslotstemplates', 
        {'cookie':session_cookie}, 
        {}, 
        ujson.dumps({'name':'automated test', 'description':'unknown description'}))
        self.assertEqual(code, 500)
        # no capacity
        result, code  = appsrc.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/recurringslotstemplates', 
        {'cookie':session_cookie}, 
        {}, 
        ujson.dumps({'name':'automated test', 'description':'unknown description', 'slotLength': 30, 'slotCapacity':''}))
        self.assertEqual(code, 500)
        # all good but wrong  lenght
        result, code  = appsrc.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/recurringslotstemplates', 
        {'cookie':session_cookie}, 
        {}, 
        ujson.dumps({'name':'automated test', 'description':'unknown description', 'slotLength': 33, 'slotCapacity': 5}))
        self.assertEqual(code, 500)
        # all good
        result, code  = appsrc.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/recurringslotstemplates', 
        {'cookie':session_cookie}, 
        {}, 
        ujson.dumps({'name':'automated test', 'description':'unknown description', 'slotLength': 30, 'slotCapacity': 5}))
        self.assertEqual(code, 200)    
        uid = result.json['id']
        self.assertGreater(len(result.json), nbRecurringSlotTemplates + 1) 
        print("####################################")
        print(result.json)
        print("id->{}".format(uid))

        #gets it    
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/recurringslotstemplates/'+uid, 
        {'cookie':session_cookie}, {}, {})
        self.assertEqual(code, 200)
        self.assertEquals(uid, result.json['id']) 

        # access unknown data
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/recurringslotstemplates/unknown', 
        {'cookie':session_cookie}, {}, {})
        self.assertEqual(code, 404)
        
        #update it
        result, code  = appsrc.tests.utils.HTTP_PUT(variables.DEFAULT_API_URL + '/recurringslotstemplates/'+uid, 
                {'cookie':session_cookie}, 
                {}, 
                ujson.dumps({'description':"test02"}))
        self.assertEqual(code, 200)
        self.assertEquals("test02", result.json['description'])
                
        #updates it with incorrect value
        result, code  = appsrc.tests.utils.HTTP_PUT(variables.DEFAULT_API_URL + '/recurringslotstemplates/'+uid, 
                {'cookie':session_cookie}, 
                {}, 
                ujson.dumps({'name':""}))
        self.assertEqual(code, 500)
        
        

