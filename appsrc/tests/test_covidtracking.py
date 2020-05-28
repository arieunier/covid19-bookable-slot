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

    def test_unauthenticated(self):
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

        result, code = appsrc.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/covidtracking', {}, {}, 
            ujson.dumps({'refDistributionPointId':distributionPointId, 'firstname':'aze','lastname':'aze','telephone':'+123123131','email':'test@test.com','numberOfPerson':5}))
        self.assertEqual(code, 200)

        #adding it to an unknown distribution id
        result, code =  appsrc.tests.utils.HTTP_POST(variables.DEFAULT_API_URL + '/covidtracking', {}, {}, 
            ujson.dumps({'refDistributionPointId':'unknown', 'firstname':'aze','lastname':'aze','telephone':'+123123131','email':'test@test.com','numberOfPerson':5}))
        self.assertEqual(code, 500)
        #tries to get the data, must fail
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/covidtracking', {}, {'refDistributionPointId':distributionPointId},{})
        self.assertEqual(code, 401)

        # now gets the admin account to retrieve all data
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/login', {"Authorization": appsrc.tests.utils.authorizationHeader(variables.DEFAULT_ADMIN_USERNAME, variables.DEFAULT_ADMIN_PASSWORD)}, {}, {})
        session_cookie=result.headers.getlist('Set-Cookie')
        self.assertIsNotNone(session_cookie)
        self.assertEqual(code, 200)
        
        # no start date, gets current day
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/covidtracking' , {'cookie':session_cookie}, {'refDistributionPointId':distributionPointId},{})
        self.assertEqual(code, 200)
        self.assertEqual(1, len(result.json))
        # with start date, gets nothing, date in the future
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/covidtracking' , {'cookie':session_cookie}, 
            {'dateStart': appsrc.tests.utils.dateToStr(appsrc.tests.utils.getTomorrowDT(), variables.DATE_PATTERN), 'refDistributionPointId':distributionPointId},{})
        self.assertEqual(code, 200)
        self.assertEqual(0, len(result.json))

     