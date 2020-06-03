from rest_framework.test import APITestCase

from model_mommy import mommy

from enhydris import models


class GareaTestCase(APITestCase):
    def setUp(self):
        self.garea = mommy.make(models.Garea)

    def test_get_garea(self):
        r = self.client.get("/api/gareas/{}/".format(self.garea.id))
        self.assertEqual(r.status_code, 200)


class OrganizationTestCase(APITestCase):
    def setUp(self):
        self.organization = mommy.make(models.Organization)

    def test_get_organization(self):
        r = self.client.get("/api/organizations/{}/".format(self.organization.id))
        self.assertEqual(r.status_code, 200)


class PersonTestCase(APITestCase):
    def setUp(self):
        self.person = mommy.make(models.Person)

    def test_get_person(self):
        r = self.client.get("/api/persons/{}/".format(self.person.id))
        self.assertEqual(r.status_code, 200)


class TimeZoneTestCase(APITestCase):
    def setUp(self):
        self.time_zone = mommy.make(models.TimeZone)

    def test_get_time_zone(self):
        r = self.client.get("/api/timezones/{}/".format(self.time_zone.id))
        self.assertEqual(r.status_code, 200)


class EventTypeTestCase(APITestCase):
    def setUp(self):
        self.event_type = mommy.make(models.EventType)

    def test_get_event_type(self):
        r = self.client.get("/api/eventtypes/{}/".format(self.event_type.id))
        self.assertEqual(r.status_code, 200)


class VariableTypeTestCase(APITestCase):
    def setUp(self):
        self.variable_type = mommy.make(models.VariableType, descr="Temperature")

    def test_get_variable_type(self):
        r = self.client.get("/api/variable_types/{}/".format(self.variable_type.id))
        self.assertEqual(r.status_code, 200)


class UnitOfMeasurementTestCase(APITestCase):
    def setUp(self):
        self.unit_of_measurement = mommy.make(models.UnitOfMeasurement)

    def test_get_unit_of_measurement(self):
        r = self.client.get("/api/units/{}/".format(self.unit_of_measurement.id))
        self.assertEqual(r.status_code, 200)


class GentityEventTestCase(APITestCase):
    # We have extensively tested GentityFile, which is practically the same code,
    # so we test this briefly.
    def setUp(self):
        self.station = mommy.make(models.Station)
        self.gentity_file = mommy.make(models.GentityEvent, gentity=self.station)

    def test_list_status_code(self):
        r = self.client.get("/api/stations/{}/events/".format(self.station.id))
        self.assertEqual(r.status_code, 200)
