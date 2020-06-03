import datetime as dt
from io import StringIO

from django.contrib.gis.geos import MultiPolygon, Point, Polygon
from django.db import IntegrityError
from django.test import TestCase, override_settings
from django.utils import translation

import pandas as pd
from htimeseries import HTimeseries
from model_mommy import mommy
from parler.utils.context import switch_language

from enhydris import models


class PersonTestCase(TestCase):
    def test_create(self):
        person = models.Person(last_name="Brown", first_name="Alice", initials="A.")
        person.save()
        self.assertEqual(models.Person.objects.first().last_name, "Brown")

    def test_update(self):
        mommy.make(models.Person)
        person = models.Person.objects.first()
        person.first_name = "Bob"
        person.save()
        self.assertEqual(models.Person.objects.first().first_name, "Bob")

    def test_delete(self):
        mommy.make(models.Person)
        person = models.Person.objects.first()
        person.delete()
        self.assertEqual(models.Person.objects.count(), 0)

    def test_str(self):
        person = mommy.make(
            models.Person, last_name="Brown", first_name="Alice", initials="A."
        )
        self.assertEqual(str(person), "Brown A.")

    def test_ordering_string(self):
        mommy.make(models.Person, last_name="Brown", first_name="Alice", initials="A.")
        person = models.Person.objects.first()
        self.assertEqual(person.ordering_string, "Brown Alice")


class OrganizationTestCase(TestCase):
    def test_create(self):
        organization = models.Organization(name="Crooks Intl", acronym="Crooks")
        organization.save()
        self.assertEqual(models.Organization.objects.first().name, "Crooks Intl")

    def test_update(self):
        mommy.make(models.Organization)
        organization = models.Organization.objects.first()
        organization.acronym = "Crooks"
        organization.save()
        self.assertEqual(models.Organization.objects.first().acronym, "Crooks")

    def test_delete(self):
        mommy.make(models.Organization)
        organization = models.Organization.objects.first()
        organization.delete()
        self.assertEqual(models.Organization.objects.count(), 0)

    def test_str(self):
        org = mommy.make(models.Organization, name="Crooks Intl", acronym="Crooks")
        self.assertEqual(str(org), "Crooks")

    def test_ordering_string(self):
        mommy.make(models.Organization, name="Crooks Intl", acronym="Crooks")
        organization = models.Organization.objects.first()
        self.assertEqual(organization.ordering_string, "Crooks Intl")


class VariableTypeTestCase(TestCase):
    def test_create(self):
        gact = models.VariableType(descr="Temperature")
        gact.save()
        self.assertEqual(models.VariableType.objects.first().descr, "Temperature")

    def test_update(self):
        mommy.make(models.VariableType, descr="Irrelevant")
        gact = models.VariableType.objects.first()
        gact.descr = "Temperature"
        gact.save()
        self.assertEqual(models.VariableType.objects.first().descr, "Temperature")

    def test_delete(self):
        mommy.make(models.VariableType, descr="Temperature")
        gact = models.VariableType.objects.first()
        gact.delete()
        self.assertEqual(models.VariableType.objects.count(), 0)

    def test_str(self):
        gact = self._create_variable_type("Temperature", "Θερμοκρασία")
        self.assertEqual(str(gact), "Temperature")
        with switch_language(gact, "el"):
            self.assertEqual(str(gact), "Θερμοκρασία")

    def test_sort(self):
        self._create_variable_type("Temperature", "Θερμοκρασία")
        self._create_variable_type("Humidity", "Υγρασία")
        self.assertEqual(
            [v.descr for v in models.VariableType.objects.all()],
            ["Humidity", "Temperature"],
        )
        with translation.override("el"):
            self.assertEqual(
                [v.descr for v in models.VariableType.objects.all()],
                ["Θερμοκρασία", "Υγρασία"],
            )

    def _create_variable_type(self, english_name, greek_name):
        mommy.make(models.VariableType, descr=english_name)
        variable_type = models.VariableType.objects.get(
            translations__descr=english_name
        )
        variable_type.translations.create(language_code="el", descr=greek_name)
        return variable_type


class GentityFileTestCase(TestCase):
    def test_create(self):
        station = mommy.make(models.Station)
        gentity_file = models.GentityFile(gentity=station, descr="North view")
        gentity_file.save()
        self.assertEqual(models.GentityFile.objects.first().descr, "North view")

    def test_update(self):
        mommy.make(models.GentityFile)
        gentity_file = models.GentityFile.objects.first()
        gentity_file.descr = "North view"
        gentity_file.save()
        self.assertEqual(models.GentityFile.objects.first().descr, "North view")

    def test_delete(self):
        mommy.make(models.GentityFile)
        gentity_file = models.GentityFile.objects.first()
        gentity_file.delete()
        self.assertEqual(models.GentityFile.objects.count(), 0)

    def test_str(self):
        gentity_file = mommy.make(models.GentityFile, descr="North view")
        self.assertEqual(str(gentity_file), "North view")

    def test_related_station(self):
        station = mommy.make(models.Station)
        gentity_file = mommy.make(models.GentityFile, gentity=station)
        self.assertEqual(gentity_file.related_station, station)

    def test_related_station_is_empty_when_gentity_is_not_station(self):
        garea = mommy.make(models.Garea)
        gentity_file = mommy.make(models.GentityFile, gentity=garea)
        self.assertIsNone(gentity_file.related_station)


class GentityEventTestCase(TestCase):
    def test_create(self):
        station = mommy.make(models.Station)
        type = mommy.make(models.EventType)
        gentity_event = models.GentityEvent(
            gentity=station,
            type=type,
            date=dt.datetime.now(),
            user="Alice",
            report="Station exploded",
        )
        gentity_event.save()
        self.assertEqual(models.GentityEvent.objects.first().report, "Station exploded")

    def test_update(self):
        mommy.make(models.GentityEvent)
        gentity_event = models.GentityEvent.objects.first()
        gentity_event.report = "Station exploded"
        gentity_event.save()
        self.assertEqual(models.GentityEvent.objects.first().report, "Station exploded")

    def test_delete(self):
        mommy.make(models.GentityEvent)
        gentity_event = models.GentityEvent.objects.first()
        gentity_event.delete()
        self.assertEqual(models.GentityEvent.objects.count(), 0)

    def test_str(self):
        gentity_event = mommy.make(
            models.GentityEvent, date="2018-11-14", type__descr="Explosion"
        )
        self.assertEqual(str(gentity_event), "2018-11-14 Explosion")

    def test_related_station(self):
        station = mommy.make(models.Station)
        gentity_event = mommy.make(models.GentityEvent, gentity=station)
        self.assertEqual(gentity_event.related_station, station)

    def test_related_station_is_empty_when_gentity_is_not_station(self):
        garea = mommy.make(models.Garea)
        gentity_event = mommy.make(models.GentityEvent, gentity=garea)
        self.assertIsNone(gentity_event.related_station)


class GareaTestCase(TestCase):
    def test_create(self):
        category = mommy.make(models.GareaCategory)
        garea = models.Garea(
            name="Esgalduin",
            category=category,
            geom=MultiPolygon(Polygon(((30, 20), (45, 40), (10, 40), (30, 20)))),
        )
        garea.save()
        self.assertEqual(models.Garea.objects.first().name, "Esgalduin")

    def test_update(self):
        mommy.make(models.Garea)
        garea = models.Garea.objects.first()
        garea.name = "Esgalduin"
        garea.save()
        self.assertEqual(models.Garea.objects.first().name, "Esgalduin")

    def test_delete(self):
        mommy.make(models.Garea)
        garea = models.Garea.objects.first()
        garea.delete()
        self.assertEqual(models.Garea.objects.count(), 0)

    def test_str(self):
        garea = mommy.make(models.Garea, name="Esgalduin")
        self.assertEqual(str(garea), "Esgalduin")


class StationTestCase(TestCase):
    def test_create(self):
        person = mommy.make(models.Person)
        station = models.Station(
            owner=person,
            copyright_holder="Bilbo Baggins",
            copyright_years="2018",
            name="Hobbiton",
            geom=Point(x=21.06071, y=39.09518, srid=4326),
        )
        station.save()
        self.assertEqual(models.Station.objects.first().name, "Hobbiton")

    def test_update(self):
        mommy.make(models.Station)
        station = models.Station.objects.first()
        station.name = "Hobbiton"
        station.save()
        self.assertEqual(models.Station.objects.first().name, "Hobbiton")

    def test_delete(self):
        mommy.make(models.Station)
        station = models.Station.objects.first()
        station.delete()
        self.assertEqual(models.Station.objects.count(), 0)

    def test_str(self):
        station = mommy.make(models.Station, name="Hobbiton")
        self.assertEqual(str(station), "Hobbiton")


class StationOriginalCoordinatesTestCase(TestCase):
    def setUp(self):
        mommy.make(
            models.Station,
            name="Komboti",
            geom=Point(x=21.06071, y=39.09518, srid=4326),
            original_srid=2100,
        )
        self.station = models.Station.objects.get(name="Komboti")

    def test_original_abscissa(self):
        self.assertAlmostEqual(self.station.original_abscissa(), 245648.96, places=1)

    def test_original_ordinate(self):
        self.assertAlmostEqual(self.station.original_ordinate(), 4331165.20, places=1)


class StationOriginalCoordinatesWithNullSridTestCase(TestCase):
    def setUp(self):
        mommy.make(
            models.Station,
            name="Komboti",
            geom=Point(x=21.06071, y=39.09518, srid=4326),
            original_srid=None,
        )
        self.station = models.Station.objects.get(name="Komboti")

    def test_original_abscissa(self):
        self.assertAlmostEqual(self.station.original_abscissa(), 21.06071)

    def test_original_ordinate(self):
        self.assertAlmostEqual(self.station.original_ordinate(), 39.09518)


class StationLastUpdateTestCase(TestCase):
    def setUp(self):
        self.station = mommy.make(models.Station)
        self.time_zone = mommy.make(models.TimeZone, code="EET", utc_offset=120)

    def _create_variable(self, ye=None, mo=None, da=None, ho=None, mi=None):
        if ye:
            end_date_utc = dt.datetime(ye, mo, da, ho, mi, tzinfo=dt.timezone.utc)
        else:
            end_date_utc = None
        variable = mommy.make(
            models.Variable,
            gentity=self.station,
            time_zone=self.time_zone,
            precision=2,
        )
        if end_date_utc:
            variable.timeseriesrecord_set.create(
                timestamp=end_date_utc, value=0, flags=""
            )

    def test_last_update_when_all_variables_have_end_date(self):
        self._create_variable(2019, 7, 24, 11, 26)
        self._create_variable(2019, 7, 23, 5, 10)
        self.assertEqual(self.station.last_update, dt.datetime(2019, 7, 24, 13, 26))

    def test_last_update_when_one_variable_has_no_data(self):
        self._create_variable(2019, 7, 24, 11, 26)
        self._create_variable()
        self.assertEqual(self.station.last_update, dt.datetime(2019, 7, 24, 13, 26))

    def test_last_update_when_all_variables_have_no_data(self):
        self._create_variable()
        self._create_variable()
        self.assertIsNone(self.station.last_update)

    def test_last_update_when_no_variable(self):
        self.assertIsNone(self.station.last_update)


class UnitOfMeasurementTestCase(TestCase):
    def test_str(self):
        unit = mommy.make(models.UnitOfMeasurement, symbol="mm")
        self.assertEqual(str(unit), "mm")

    def test_str_when_symbol_is_empty(self):
        unit = mommy.make(models.UnitOfMeasurement, symbol="")
        self.assertEqual(str(unit), str(unit.id))


class TimeZoneTestCase(TestCase):
    def test_create(self):
        time_zone = models.TimeZone(code="EET", utc_offset=120)
        time_zone.save()
        self.assertEqual(models.TimeZone.objects.first().code, "EET")

    def test_update(self):
        mommy.make(models.TimeZone)
        time_zone = models.TimeZone.objects.first()
        time_zone.code = "EET"
        time_zone.save()
        self.assertEqual(models.TimeZone.objects.first().code, "EET")

    def test_delete(self):
        mommy.make(models.TimeZone)
        time_zone = models.TimeZone.objects.first()
        time_zone.delete()
        self.assertEqual(models.TimeZone.objects.count(), 0)

    def test_str(self):
        time_zone = mommy.make(models.TimeZone, code="EET", utc_offset=120)
        self.assertEqual(str(time_zone), "EET (UTC+0200)")

    def test_as_tzinfo(self):
        time_zone = mommy.make(models.TimeZone, code="EET", utc_offset=120)
        self.assertEqual(time_zone.as_tzinfo, dt.timezone(dt.timedelta(hours=2), "EET"))


class TimeseriesTestCase(TestCase):
    def test_create(self):
        station = mommy.make(models.Station)
        variable_type = mommy.make(models.VariableType)
        unit = mommy.make(models.UnitOfMeasurement)
        time_zone = mommy.make(models.TimeZone)
        variable = models.Timeseries(
            gentity=station,
            name="Temperature",
            variable_type=variable_type,
            unit_of_measurement=unit,
            time_zone=time_zone,
            precision=2,
        )
        variable.save()
        self.assertEqual(models.Timeseries.objects.first().name, "Temperature")

    def test_update(self):
        mommy.make(models.Timeseries)
        variable = models.Timeseries.objects.first()
        variable.name = "Temperature"
        variable.save()
        self.assertEqual(models.Timeseries.objects.first().name, "Temperature")

    def test_delete(self):
        mommy.make(models.Timeseries)
        variable = models.Timeseries.objects.first()
        variable.delete()
        self.assertEqual(models.Timeseries.objects.count(), 0)

    def test_str(self):
        variable = mommy.make(models.Timeseries, name="Temperature")
        self.assertEqual(str(variable), "Temperature")

    def test_related_station(self):
        station = mommy.make(models.Station)
        variable = mommy.make(models.Timeseries, gentity=station)
        self.assertEqual(variable.related_station, station)


def make_variable(*, start_date, end_date, **kwargs):
    """Make a test variable, setting start_date and end_date.
    This is essentially the same as mommy.make(models.Timeseries, **kwargs), except
    that it also creates two records with the specified dates.
    """
    result = mommy.make(models.Timeseries, **kwargs)
    result.timeseriesrecord_set.create(timestamp=start_date, value=0, flags="")
    result.timeseriesrecord_set.create(timestamp=end_date, value=0, flags="")
    return result


class TimeseriesDatesTestCase(TestCase):
    def setUp(self):
        self.variable = make_variable(
            time_zone__utc_offset=120,
            precision=2,
            start_date=dt.datetime(2018, 11, 15, 16, 0, tzinfo=dt.timezone.utc),
            end_date=dt.datetime(2018, 11, 17, 23, 0, tzinfo=dt.timezone.utc),
        )

    def test_start_date(self):
        self.assertEqual(
            self.variable.start_date,
            dt.datetime(
                2018, 11, 15, 18, 0, tzinfo=self.variable.time_zone.as_tzinfo
            ),
        )

    def test_start_date_tzinfo(self):
        self.assertEqual(
            self.variable.start_date.tzinfo, self.timeseries.time_zone.as_tzinfo
        )

    def test_end_date(self):
        self.assertEqual(
            self.variable.end_date,
            dt.datetime(2018, 11, 18, 1, 0, tzinfo=self.variable.time_zone.as_tzinfo),
        )

    def test_end_date_tzinfo(self):
        self.assertEqual(
            self.variable.end_date.tzinfo, self.variable.time_zone.as_tzinfo
        )

    def test_start_date_naive(self):
        self.assertEqual(
            self.variable.start_date_naive, dt.datetime(2018, 11, 15, 18, 0),
        )

    def test_end_date_naive(self):
        self.assertEqual(
            self.variable.end_date_naive, dt.datetime(2018, 11, 18, 1, 0),
        )


class DataTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        station = mommy.make(
            models.Station,
            name="Celduin",
            original_srid=2100,
            geom=Point(x=21.06071, y=39.09518, srid=4326),
            altitude=219,
        )
        cls.variable = mommy.make(
            models.Timeseries,
            name="Daily temperature",
            gentity=station,
            time_step="H",
            unit_of_measurement__symbol="mm",
            time_zone__code="IST",
            time_zone__utc_offset=330,
            variable_type__descr="Temperature",
            precision=1,
            remarks="This variable rocks",
        )
        cls.variable.set_data(StringIO("2017-11-23 17:23,1,\n2018-11-25 01:00,2,\n"))

        cls.expected_result = pd.DataFrame(
            data={"value": [1.0, 2.0], "flags": ["", ""]},
            columns=["value", "flags"],
            index=[dt.datetime(2017, 11, 23, 17, 23), dt.datetime(2018, 11, 25, 1, 0)],
        )
        cls.expected_result.index.name = "date"


class TimeseriesGetDataTestCase(DataTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.data = cls.variable.get_data()

    def test_abscissa(self):
        self.assertAlmostEqual(self.data.location["abscissa"], 245648.96, places=2)

    def test_ordinate(self):
        self.assertAlmostEqual(self.data.location["ordinate"], 4331165.20, places=2)

    def test_srid(self):
        self.assertAlmostEqual(self.data.location["srid"], 2100)

    def test_altitude(self):
        self.assertAlmostEqual(self.data.location["altitude"], 219)

    def test_time_step(self):
        self.assertEqual(self.data.time_step, "H")

    def test_unit(self):
        self.assertEqual(self.data.unit, "mm")

    def test_title(self):
        self.assertEqual(self.data.title, "Daily temperature")

    def test_timezone(self):
        self.assertEqual(self.data.timezone, "IST (UTC+0530)")

    def test_negative_timezone(self):
        self.variable.time_zone.code = "NST"
        self.variable.time_zone.utc_offset = -210
        data = self.variable.get_data()
        self.assertEqual(data.timezone, "NST (UTC-0330)")

    def test_variable_type(self):
        self.assertEqual(self.data.variable_type, "Temperature")

    def test_precision(self):
        self.assertEqual(self.data.precision, 1)

    def test_comment(self):
        self.assertEqual(self.data.comment, "Celduin\n\nThis variable rocks")

    def test_location_is_none(self):
        self.variable.gentity.geom = None
        data = self.variable.get_data()
        self.assertIsNone(data.location)

    def test_data(self):
        pd.testing.assert_frame_equal(self.data.data, self.expected_result)


class TimeseriesGetDataWithStartAndEndDateTestCase(DataTestCase):
    def _check(self, start_index=None, end_index=None):
        """Check self.htimeseries.data against the initial timeseries sliced from
        start_index to end_index.
        """
        full_result = pd.DataFrame(
            data={"value": [1.0, 2.0], "flags": ["", ""]},
            columns=["value", "flags"],
            index=[dt.datetime(2017, 11, 23, 17, 23), dt.datetime(2018, 11, 25, 1, 0)],
        )
        full_result.index.name = "date"
        expected_result = full_result.iloc[start_index:end_index]
        pd.testing.assert_frame_equal(self.ahtimeseries.data, expected_result)

    def test_with_start_date_just_before_start_of_timeseries(self):
        tzinfo = self.variable.time_zone.as_tzinfo
        start_date = dt.datetime(2017, 11, 23, 17, 22, tzinfo=tzinfo)
        self.ahtimeseries = self.variable.get_data(start_date=start_date)
        self._check()

    def test_with_start_date_on_start_of_timeseries(self):
        tzinfo = self.variable.time_zone.as_tzinfo
        start_date = dt.datetime(2017, 11, 23, 17, 23, tzinfo=tzinfo)
        self.ahtimeseries = self.variable.get_data(start_date=start_date)
        self._check()

    def test_with_start_date_just_after_start_of_timeseries(self):
        tzinfo = self.variable.time_zone.as_tzinfo
        start_date = dt.datetime(2017, 11, 23, 17, 24, tzinfo=tzinfo)
        self.ahtimeseries = self.variable.get_data(start_date=start_date)
        self._check(start_index=1)

    def test_with_end_date_just_after_end_of_timeseries(self):
        tzinfo = self.variable.time_zone.as_tzinfo
        end_date = dt.datetime(2018, 11, 25, 1, 1, tzinfo=tzinfo)
        self.ahtimeseries = self.variable.get_data(end_date=end_date)
        self._check()

    def test_with_end_date_on_end_of_timeseries(self):
        tzinfo = self.variable.time_zone.as_tzinfo
        end_date = dt.datetime(2018, 11, 25, 1, 0, tzinfo=tzinfo)
        self.ahtimeseries = self.variable.get_data(end_date=end_date)
        self._check()

    def test_with_end_date_just_before_end_of_timeseries(self):
        tzinfo = self.variable.time_zone.as_tzinfo
        end_date = dt.datetime(2018, 11, 25, 0, 59, tzinfo=tzinfo)
        self.ahtimeseries = self.variable.get_data(end_date=end_date)
        self._check(end_index=1)


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
)
class TimeseriesGetDataCacheTestCase(DataTestCase):
    def test_cache(self):
        # Make sure we've accessed gpoint already, otherwise it screws up the number of
        # queries later
        self.variable.gentity.gpoint.altitude

        self._get_data_and_check_num_queries(1)
        self._get_data_and_check_num_queries(0)

        # Check cache invalidation
        self.variable.save()
        self._get_data_and_check_num_queries(1)

    def _get_data_and_check_num_queries(self, num_queries):
        with self.assertNumQueries(num_queries):
            data = self.variable.get_data()
        pd.testing.assert_frame_equal(data.data, self.expected_result)


class TimeseriesSetDataTestCase(TestCase):
    def setUp(self):
        self.variable = mommy.make(
            models.Timeseries, id=42, time_zone__utc_offset=0, precision=2
        )

    def test_call_with_file_object(self):
        self.returned_length = self.variable.set_data(
            StringIO("2017-11-23 17:23,1,\n" "2018-11-25 01:00,2,\n")
        )
        self._check_results()

    def test_call_with_dataframe(self):
        self.returned_length = self.variable.set_data(self._get_dataframe())
        self._check_results()

    def test_call_with_htimeseries(self):
        self.returned_length = self.variable.set_data(
            HTimeseries(self._get_dataframe())
        )
        self._check_results()

    def _get_dataframe(self):
        result = pd.DataFrame(
            data={"value": [1.0, 2.0], "flags": ["", ""]},
            columns=["value", "flags"],
            index=[dt.datetime(2017, 11, 23, 17, 23), dt.datetime(2018, 11, 25, 1, 0)],
        )
        result.index.name = "date"
        return result

    def _check_results(self):
        self.assertEqual(self.returned_length, 2)
        self.assertEqual(
            list(self.variable.timeseriesrecord_set.values()),
            [
                {
                    "variable_id": 42,
                    "timestamp": dt.datetime(
                        2017, 11, 23, 17, 23, tzinfo=dt.timezone.utc
                    ),
                    "value": 1.0,
                    "flags": "",
                },
                {
                    "variable_id": 42,
                    "timestamp": dt.datetime(
                        2018, 11, 25, 1, 0, tzinfo=dt.timezone.utc
                    ),
                    "value": 2.0,
                    "flags": "",
                },
            ],
        )


class TimeseriesAppendDataTestCase(TestCase):
    def setUp(self):
        station = mommy.make(models.Station)
        self.variable = mommy.make(
            models.Timeseries,
            gentity=station,
            id=42,
            time_zone__utc_offset=0,
            precision=2,
            variable_type__descr="Temperature",
        )
        self.variable.set_data(StringIO("2016-01-01 00:00,42,\n"))

    def test_call_with_file_object(self):
        returned_length = self.variable.append_data(
            StringIO("2017-11-23 17:23,1,\n" "2018-11-25 01:00,2,\n")
        )
        self.assertEqual(returned_length, 2)
        self._assert_wrote_data()

    def test_call_with_dataframe(self):
        returned_length = self.variable.append_data(self._get_dataframe())
        self.assertEqual(returned_length, 2)
        self._assert_wrote_data()

    def test_call_with_htimeseries(self):
        returned_length = self.variable.append_data(
            HTimeseries(self._get_dataframe())
        )
        self.assertEqual(returned_length, 2)
        self._assert_wrote_data()

    def _get_dataframe(self):
        result = pd.DataFrame(
            data={"value": [1.0, 2.0], "flags": ["", ""]},
            columns=["value", "flags"],
            index=[dt.datetime(2017, 11, 23, 17, 23), dt.datetime(2018, 11, 25, 1, 0)],
        )
        result.index.name = "date"
        return result

    def _assert_wrote_data(self):
        expected_result = pd.DataFrame(
            data={"value": [42.0, 1.0, 2.0], "flags": ["", "", ""]},
            columns=["value", "flags"],
            index=[
                dt.datetime(2016, 1, 1, 0, 0),
                dt.datetime(2017, 11, 23, 17, 23),
                dt.datetime(2018, 11, 25, 1, 0),
            ],
        )
        expected_result.index.name = "date"
        pd.testing.assert_frame_equal(self.variable.get_data().data, expected_result)


class TimeseriesAppendDataToEmptyTimeseriesTestCase(TestCase):
    def setUp(self):
        station = mommy.make(models.Station)
        self.variable = mommy.make(
            models.Timeseries,
            gentity=station,
            id=42,
            time_zone__utc_offset=0,
            precision=2,
            variable_type__descr="Temperature",
        )

    def test_call_with_dataframe(self):
        returned_length = self.variable.append_data(self._get_dataframe())
        self.assertEqual(returned_length, 2)
        self._assert_wrote_data()

    def _get_dataframe(self):
        result = pd.DataFrame(
            data={"value": [1.0, 2.0], "flags": ["", ""]},
            columns=["value", "flags"],
            index=[dt.datetime(2017, 11, 23, 17, 23), dt.datetime(2018, 11, 25, 1, 0)],
        )
        result.index.name = "date"
        return result

    def _assert_wrote_data(self):
        pd.testing.assert_frame_equal(
            self.variable.get_data().data, self._get_dataframe()
        )


class TimeseriesAppendErrorTestCase(TestCase):
    def test_does_not_update_if_data_to_append_are_not_later(self):
        self.variable = mommy.make(
            models.Timeseries, id=42, time_zone__utc_offset=0, precision=2
        )
        self.variable.set_data(StringIO("2018-01-01 00:00,42,\n"))
        with self.assertRaises(IntegrityError):
            self.variable.append_data(
                StringIO("2017-11-23 17:23,1,\n2018-11-25 01:00,2,\n")
            )


class TimeseriesGetLastRecordAsStringTestCase(TestCase):
    def test_when_record_exists(self):
        variable = mommy.make(
            models.Timeseries, id=42, time_zone__utc_offset=0, precision=2
        )
        variable.set_data(StringIO("2017-11-23 17:23,1,\n2018-11-25 01:00,2,\n"))
        self.assertEqual(
            variable.get_last_record_as_string(), "2018-11-25 01:00,2.00,"
        )

    def test_when_record_does_not_exist(self):
        variable = mommy.make(
            models.Timeseries, id=42, time_zone__utc_offset=0, precision=2
        )
        self.assertEqual(variable.get_last_record_as_string(), "")


class TimestepTestCase(TestCase):
    def setUp(self):
        self.variable = mommy.make(models.Timeseries)

    def set_time_step(self, time_step):
        self.variable.time_step = time_step
        self.variable.save()

    def test_min(self):
        self.set_time_step("27min")
        self.assertEqual(models.Timeseries.objects.first().time_step, "27min")

    def test_hour(self):
        self.set_time_step("3H")
        self.assertEqual(models.Timeseries.objects.first().time_step, "3H")

    def test_day(self):
        self.set_time_step("3D")
        self.assertEqual(models.Timeseries.objects.first().time_step, "3D")

    def test_month(self):
        self.set_time_step("3M")
        self.assertEqual(models.Timeseries.objects.first().time_step, "3M")

    def test_3Y(self):
        self.set_time_step("3Y")
        self.assertEqual(models.Timeseries.objects.first().time_step, "3Y")

    def test_Y(self):
        self.set_time_step("Y")
        self.assertEqual(models.Timeseries.objects.first().time_step, "Y")

    def test_garbage(self):
        with self.assertRaisesRegex(ValueError, '"hello" is not a valid time step'):
            self.set_time_step("hello")

    def test_wrong_number(self):
        with self.assertRaisesRegex(ValueError, '"FM" is not a valid time step'):
            self.set_time_step("FM")

    def test_wrong_unit(self):
        with self.assertRaisesRegex(ValueError, '"3B" is not a valid time step'):
            self.set_time_step("3B")


class TimeseriesRecordTestCase(TestCase):
    def setUp(self):
        variable = mommy.make(
            models.Timeseries,
            time_step="H",
            time_zone__code="IST",
            time_zone__utc_offset=330,
            precision=2,
        )
        variable.set_data(StringIO("2017-11-23 17:23,3.14159,\n"))

    def test_str(self):
        record = models.TimeseriesRecord.objects.first()
        self.assertAlmostEqual(record.value, 3.14159)
        self.assertEqual(str(record), "2017-11-23 17:23,3.14,")
