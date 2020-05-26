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

    def test_login(self):
        # not event log/pwd in header
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/login', {}, {}, {})        
        self.assertEqual(code, 401)

        # unknown user/pwd
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/login', {"Authorization": appsrc.tests.utils.authorizationHeader('idont', 'exist')}, {}, {})        
        self.assertEqual(code, 404)
        # correct user/pwd
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/login', {"Authorization": appsrc.tests.utils.authorizationHeader(variables.DEFAULT_ADMIN_USERNAME, variables.DEFAULT_ADMIN_PASSWORD)}, {}, {})
        session_cookie=result.headers.getlist('Set-Cookie')
        self.assertIsNotNone(session_cookie)
        self.assertEqual(code, 200)
        #second time it must be wrong
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/login', {"Authorization": appsrc.tests.utils.authorizationHeader(variables.DEFAULT_ADMIN_USERNAME, variables.DEFAULT_ADMIN_PASSWORD), 'Cookie':session_cookie}, {}, {})        
        self.assertEqual(code, 404)
        #logout
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/logout', {"Authorization": appsrc.tests.utils.authorizationHeader(variables.DEFAULT_ADMIN_USERNAME, variables.DEFAULT_ADMIN_PASSWORD)}, {}, {})
        session_cookie=result.headers.getlist('Set-Cookie')
        self.assertIsNotNone(session_cookie)
        self.assertEqual(code, 200)
        # can't logout 
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/logout', {"Authorization": appsrc.tests.utils.authorizationHeader('idont', 'exist')}, {}, {})        
        self.assertEqual(code, 200)