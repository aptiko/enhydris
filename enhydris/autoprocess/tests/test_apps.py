from unittest import mock

from django.db import transaction
from django.test import TransactionTestCase

from model_bakery import baker

from enhydris.autoprocess.models import Checks
from enhydris.models import Station, Timeseries


class EnqueueAutoProcessTestCase(TransactionTestCase):
    # Setting available_apps activates TRUNCATE ... CASCADE, which is necessary because
    # enhydris.TimeseriesRecord is unmanaged, TransactionTestCase doesn't attempt to
    # truncate it, and PostgreSQL complains it can't truncate enhydris_timeseries
    # without truncating enhydris_timeseriesrecord at the same time.
    available_apps = ["django.contrib.sites", "enhydris", "enhydris.autoprocess"]

    def setUp(self):
        self.station = baker.make(Station)
        self.auto_process = baker.make(
            Checks,
            timeseries_group__gentity=self.station,
            target_timeseries_group__gentity=self.station,
        )
        self.timeseries = baker.make(
            Timeseries,
            timeseries_group=self.auto_process.timeseries_group,
            type=Timeseries.INITIAL,
        )

    @mock.patch("enhydris.autoprocess.apps.execute_auto_process")
    def test_enqueues_auto_process(self, m):
        with transaction.atomic():
            self.timeseries.save()
        m.delay.assert_any_call(self.auto_process.id)

    @mock.patch("enhydris.autoprocess.apps.execute_auto_process")
    def test_auto_process_is_not_triggered_before_commit(self, m):
        with transaction.atomic():
            self.timeseries.save()
            m.delay.assert_not_called()
