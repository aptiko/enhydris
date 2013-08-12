from datetime import datetime
import json

from django.test import TestCase
from django.test.client import MULTIPART_CONTENT, BOUNDARY, encode_multipart
from django.db import connection
from pthelma.timeseries import Timeseries
from enhydris.hcore import models


class WriteTestCase(TestCase):
    fixtures = ['enhydris/api/testdata.json']

    def testTimeSeries(self):
        # Get an existing time series
        obj = models.Timeseries.objects.filter(name='Test Timeseries')[0]
        response = self.client.get("/api/Timeseries/%d/" % (obj.id,))
        t = json.loads(response.content)

        # Change some of its attributes
        t['id'] = None
        t['name'] = "Test Timeseries 1221"
        t['remarks'] = "Yet another timeseries test"

        # Attempt to upload unauthenticated - should deny
        d = json.dumps(t)
        response = self.client.post("/api/Timeseries/", data=d,
                                    content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(models.Timeseries.objects.filter(
                                    name='Test Timeseries 1221').count(), 0)

        # Now try again, this time logged on as user 2; again should deny
        self.assert_(self.client.login(username='user2', password='password2'))
        response = self.client.post("/api/Timeseries/", data=d,
                                            content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(models.Timeseries.objects.filter(
                                    name='Test Timeseries 1221').count(), 0)
        self.client.logout()

        # Now try again, this time logged on as user 1; should accept
        self.assert_(self.client.login(username='user1', password='password1'))
        response = self.client.post("/api/Timeseries/", data=d,
                                            content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(models.Timeseries.objects.filter(
                                    name='Test Timeseries 1221').count(), 1)
        self.client.logout()

    def testTimeseriesDelete(self):
        # Check the number of timeseries available
        ntimeseries = models.Timeseries.objects.count()
        assert(ntimeseries > 1) # 1 is not enough; we need to know we aren't
                                # deleting more than necessary.

        # Attempt to delete unauthenticated - should fail
        response = self.client.delete("/api/Timeseries/1/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(models.Timeseries.objects.filter(pk=1).count(), 1)
        self.assertEqual(models.Timeseries.objects.count(), ntimeseries)

        # Try again as user2 - should fail
        self.assert_(self.client.login(username='user2', password='password2'))
        response = self.client.delete("/api/Timeseries/1/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(models.Timeseries.objects.filter(pk=1).count(), 1)
        self.assertEqual(models.Timeseries.objects.count(), ntimeseries)
        self.client.logout()

        # Try again as user1 - should succeed
        self.assert_(self.client.login(username='user1', password='password1'))
        response = self.client.delete("/api/Timeseries/1/")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(models.Timeseries.objects.filter(pk=1).count(), 0)
        self.assertEqual(models.Timeseries.objects.count(), ntimeseries-1)
        self.client.logout()

    def testUploadTsDataUnauthenticated(self):
        # Attempt to upload some timeseries data, unauthenticated
        response = self.client.put(
            "/api/tsdata/1/",
            encode_multipart(BOUNDARY,
                             {'timeseries_records': '2012-11-06 18:17,20,\n'}),
            content_type=MULTIPART_CONTENT)
        t = Timeseries(1)
        t.read_from_db(connection)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(t), 0)

    def testUploadTsDataAsWrongUser(self):
        # Attempt to upload some timeseries data as user 2; should deny
        self.assert_(self.client.login(username='user2', password='password2'))
        response = self.client.put(
            "/api/tsdata/1/",
            encode_multipart(BOUNDARY,
                             {'timeseries_records': '2012-11-06 18:17,20,\n'}),
            content_type=MULTIPART_CONTENT)
        t = Timeseries(1)
        t.read_from_db(connection)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(t), 0)
        self.client.logout()

    def testUploadTsDataGarbage(self):
        self.assert_(self.client.login(username='user1', password='password1'))
        response = self.client.put(
            "/api/tsdata/1/",
            encode_multipart(BOUNDARY,
                             {'timeseries_records': '2012-aa-06 18:17,20,\n'}),
            content_type=MULTIPART_CONTENT)
        t = Timeseries(1)
        t.read_from_db(connection)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(t), 0)
        self.client.logout()

    def testUploadTsData(self):
        self.assert_(self.client.login(username='user1', password='password1'))
        response = self.client.put(
            "/api/tsdata/1/",
            encode_multipart(BOUNDARY,
                             {'timeseries_records': '2012-11-06 18:17,20,\n'}),
            content_type=MULTIPART_CONTENT)
        t = Timeseries(1)
        t.read_from_db(connection)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '1')
        self.assertEqual(len(t), 1)
        self.assertEqual(t.items(0)[0], datetime(2012, 11, 06, 18, 17, 0))
        self.assertEqual(t.items(0)[1], 20)
        self.client.logout()

        # Append two more records
        self.assert_(self.client.login(username='user1', password='password1'))
        response = self.client.put(
            "/api/tsdata/1/",
            encode_multipart(BOUNDARY,
                             {'timeseries_records':
                              '2012-11-06 18:18,21,\n2012-11-07 18:18,23,\n' }),
            content_type=MULTIPART_CONTENT)
        t = Timeseries(1)
        t.read_from_db(connection)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '2')
        self.assertEqual(len(t), 3)
        self.assertEqual(t.items(0)[0], datetime(2012, 11, 06, 18, 17, 0))
        self.assertEqual(t.items(0)[1], 20)
        self.assertEqual(t.items(1)[0], datetime(2012, 11, 06, 18, 18, 0))
        self.assertEqual(t.items(1)[1], 21)
        self.assertEqual(t.items(2)[0], datetime(2012, 11, 07, 18, 18, 0))
        self.assertEqual(t.items(2)[1], 23)
        self.client.logout()

        # Try to append an earlier record; should fail
        self.assert_(self.client.login(username='user1', password='password1'))
        response = self.client.put(
            "/api/tsdata/1/",
            encode_multipart(BOUNDARY,
                             {'timeseries_records': '2012-11-05 18:18,21,\n'}),
            content_type=MULTIPART_CONTENT)
        self.client.logout()
        t = Timeseries(1)
        t.read_from_db(connection)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(len(t), 3)
        self.client.logout()
