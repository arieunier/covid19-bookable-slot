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
        self.assertEqual(len(result.json), 2)

        # access bslots with correct dp, date in a day from current time
        tomorrow = (datetime.now() + timedelta(days=1)).strftime(variables.DATE_PATTERN)
        result, code = appsrc.tests.utils.HTTP_GET(variables.DEFAULT_API_URL + '/bookableslots/' + distributionPointId, {}, {'dateStart':tomorrow}, {})
        self.assertEqual(code, 200)
        self.assertEqual(len(result.json), 1)
    

    def test_access_authenticated(self):    
        pass