from datetime import timedelta, timezone
from itertools import islice

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.core.cache import cache
from django.core.files.storage import FileSystemStorage
from django.db import IntegrityError
from django.db.models.signals import post_save
from django.utils._os import abspathu
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

import pandas as pd
from htimeseries import HTimeseries
from parler.managers import TranslatableManager
from parler.models import TranslatableModel, TranslatedFields


def check_time_step(time_step):
    if not time_step:
        return
    else:
        _check_nonempty_time_step(time_step)


def _check_nonempty_time_step(time_step):
    number, unit = _parse_time_step(time_step)
    if unit not in ("min", "H", "D", "M", "Y"):
        raise ValueError('"{}" is not a valid time step'.format(time_step))


def _parse_time_step(time_step):
    first_nondigit_pos = 0
    length = len(time_step)
    while first_nondigit_pos < length and time_step[first_nondigit_pos].isdigit():
        first_nondigit_pos += 1
    number = time_step[:first_nondigit_pos]
    unit = time_step[first_nondigit_pos:]
    return number, unit


#
# Lookups
#


class Lookup(models.Model):
    last_modified = models.DateTimeField(default=now, null=True, editable=False)
    descr = models.CharField(max_length=200, blank=True)

    class Meta:
        abstract = True
        ordering = ("descr",)

    def __str__(self):
        return self.descr


#
# Lentity and descendants
#


def post_save_person_or_organization(sender, **kwargs):
    """Create and save ordering_string upon saving a person or organization.

    When we want to sort a list of lentities that has both people and organizations,
    we need a common sorting field. We calculate and save this sorting field upon
    saving the person or organization.
    """
    instance = kwargs["instance"]
    try:
        string = instance.name
    except AttributeError:
        string = "{} {}".format(instance.last_name, instance.first_name)
    lentity = instance.lentity_ptr
    lentity.ordering_string = string
    super(Lentity, lentity).save()


class Lentity(models.Model):
    last_modified = models.DateTimeField(default=now, null=True, editable=False)
    remarks = models.TextField(blank=True)
    ordering_string = models.CharField(
        max_length=255, null=True, blank=True, editable=False
    )

    class Meta:
        verbose_name_plural = "Lentities"
        ordering = ("ordering_string",)

    def __str__(self):
        return self.ordering_string or str(self.pk)


class Person(Lentity):
    last_name = models.CharField(max_length=100, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    middle_names = models.CharField(max_length=100, blank=True)
    initials = models.CharField(max_length=20, blank=True)
    f_dependencies = ["Lentity"]

    class Meta:
        ordering = ("last_name", "first_name")

    def __str__(self):
        return self.last_name + " " + self.initials


post_save.connect(post_save_person_or_organization, sender=Person)


class Organization(Lentity):
    name = models.CharField(max_length=200, blank=True)
    acronym = models.CharField(max_length=50, blank=True)
    f_dependencies = ["Lentity"]

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.acronym if self.acronym else self.name


post_save.connect(post_save_person_or_organization, sender=Organization)


#
# Gentity and direct descendants
#


class Gentity(models.Model):
    last_modified = models.DateTimeField(default=now, null=True, editable=False)
    name = models.CharField(max_length=200, blank=True)
    code = models.CharField(max_length=50, blank=True)
    remarks = models.TextField(blank=True)
    geom = models.GeometryField()

    class Meta:
        verbose_name_plural = "Gentities"
        ordering = ("name",)

    def __str__(self):
        return self.name or self.code or str(self.id)


class Gpoint(Gentity):
    original_srid = models.IntegerField(null=True, blank=True)
    altitude = models.FloatField(null=True, blank=True)
    f_dependencies = ["Gentity"]

    def original_abscissa(self):
        if self.original_srid:
            (x, y) = self.geom.transform(self.original_srid, clone=True)
            return round(x, 2) if abs(x) > 180 and abs(y) > 90 else x
        else:
            return self.geom.x

    def original_ordinate(self):
        if self.original_srid:
            (x, y) = self.geom.transform(self.original_srid, clone=True)
            return round(y, 2) if abs(x) > 180 and abs(y) > 90 else y
        else:
            return self.geom.y


class GareaCategory(Lookup):
    class Meta:
        verbose_name = "Garea categories"
        verbose_name_plural = "Garea categories"


class Garea(Gentity):
    category = models.ForeignKey(GareaCategory, on_delete=models.CASCADE)
    f_dependencies = ["Gentity"]


#
# Gentity-related models
#


class GentityFile(models.Model):
    last_modified = models.DateTimeField(default=now, null=True, editable=False)
    gentity = models.ForeignKey(Gentity, on_delete=models.CASCADE)
    date = models.DateField(blank=True, null=True)
    content = models.FileField(upload_to="gentityfile")
    descr = models.CharField(max_length=100)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ("descr",)
        verbose_name = _("File")
        verbose_name_plural = _("Files")

    def __str__(self):
        return self.descr or str(self.id)

    @property
    def related_station(self):
        try:
            return Station.objects.get(id=self.gentity.id)
        except Station.DoesNotExist:
            return None


class EventType(Lookup):
    pass


class GentityEvent(models.Model):
    last_modified = models.DateTimeField(default=now, null=True, editable=False)
    gentity = models.ForeignKey(Gentity, on_delete=models.CASCADE)
    date = models.DateField()
    type = models.ForeignKey(EventType, on_delete=models.CASCADE)
    user = models.CharField(blank=True, max_length=64)
    report = models.TextField(blank=True)

    class Meta:
        ordering = ["-date"]
        verbose_name = _("Log entry")
        verbose_name_plural = _("Log entries")

    def __str__(self):
        return str(self.date) + " " + self.type.__str__()

    @property
    def related_station(self):
        try:
            return Station.objects.get(id=self.gentity.id)
        except Station.DoesNotExist:
            return None


#
# Station and its related models
#


class Station(Gpoint):
    owner = models.ForeignKey(
        Lentity, related_name="owned_stations", on_delete=models.CASCADE
    )
    is_automatic = models.BooleanField(default=False)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    overseer = models.CharField(max_length=30, blank=True)
    copyright_holder = models.TextField()
    copyright_years = models.CharField(max_length=10)
    # The following two fields are only useful when USERS_CAN_ADD_CONTENT
    # is set.
    creator = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="created_stations",
        on_delete=models.CASCADE,
    )
    maintainers = models.ManyToManyField(
        User, blank=True, related_name="maintaining_stations"
    )

    f_dependencies = ["Gpoint"]

    @property
    def last_update(self):
        timeseries = Timeseries.objects.filter(gentity_id=self.id)
        result = None
        for t in timeseries:
            try:
                latest_record = TimeseriesRecord.objects.filter(
                    timeseries_id=t.id
                ).latest()
            except TimeseriesRecord.DoesNotExist:
                continue
            latest_timestamp = latest_record.timestamp.astimezone(
                t.time_zone.as_tzinfo
            ).replace(tzinfo=None)

            if result is None or latest_timestamp > result:
                result = latest_timestamp
        return result


#
# Time series and related models
#


class VariableTypeManager(TranslatableManager):
    def get_queryset(self):
        return super().get_queryset().translated().order_by("translations__descr")


class VariableType(TranslatableModel):
    last_modified = models.DateTimeField(default=now, null=True, editable=False)
    translations = TranslatedFields(descr=models.CharField(max_length=200, blank=True))

    objects = VariableTypeManager()

    def __str__(self):
        return self.descr


class UnitOfMeasurement(Lookup):
    symbol = models.CharField(max_length=50)
    variable_types = models.ManyToManyField(VariableType)

    def __str__(self):
        if self.symbol:
            return self.symbol
        return str(self.id)

    class Meta:
        ordering = ["symbol"]


class TimeZone(models.Model):
    last_modified = models.DateTimeField(default=now, null=True, editable=False)
    code = models.CharField(max_length=50)
    utc_offset = models.SmallIntegerField()

    @property
    def as_tzinfo(self):
        return timezone(timedelta(minutes=self.utc_offset), self.code)

    def __str__(self):
        return "%s (UTC%+03d%02d)" % (
            self.code,
            (abs(self.utc_offset) / 60) * (-1 if self.utc_offset < 0 else 1),
            abs(self.utc_offset % 60),
        )

    class Meta:
        ordering = ("utc_offset",)


class TimeseriesStorage(FileSystemStorage):
    """Stores timeseries data files in settings.ENHYDRIS_TIMESERIES_DATA_DIR.

    TimeseriesStorage() is essentially the same as
    FileSystemStorage(location=settings.ENHYDRIS_TIMESERIES_DATA_DIR)), with
    the difference that it checks the value of ENHYDRIS_TIMESERIES_DATA_DIR
    each time it does something. This allows the setting to be overridden
    in unit tests with override_settings(). If using FileSystemStorage,
    it would not be overriddable, because "location" would be set when
    models.py is read and that would be it.
    """

    def path(self, name):
        self.location = abspathu(settings.ENHYDRIS_TIMESERIES_DATA_DIR)
        return super().path(name)


class Timeseries(models.Model):
    last_modified = models.DateTimeField(default=now, null=True, editable=False)
    gentity = models.ForeignKey(
        Gentity, related_name="timeseries", on_delete=models.CASCADE
    )
    variable_type = models.ForeignKey(VariableType, on_delete=models.CASCADE)
    unit_of_measurement = models.ForeignKey(UnitOfMeasurement, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, blank=True)
    hidden = models.BooleanField(null=False, blank=False, default=False)
    precision = models.SmallIntegerField(
        help_text=_(
            "The number of decimal digits to which the values of the time series "
            "will be rounded. It's usually positive, but it can be zero or negative; "
            "for example, for humidity it is usually zero; for wind direction in "
            "degrees, depending on the sensor, you might want to specify "
            "precision -1, which means the value will be 10, or 20, or 30, etc. This "
            "only affects the rounding of values when the time series is retrieved; "
            "values are always stored with all the decimal digits provided."
        )
    )
    time_zone = models.ForeignKey(TimeZone, on_delete=models.CASCADE)
    remarks = models.TextField(blank=True)
    time_step = models.CharField(
        max_length=7,
        blank=True,
        help_text=_(
            'E.g. "10min", "H" (hourly), "D" (daily), "M" (monthly), "Y" (yearly). '
            "More specifically, it's an optional number plus a unit, with no space in "
            "between. The units available are min, H, D, M, Y. Leave empty if the time "
            "series is irregular."
        ),
    )

    class Meta:
        verbose_name = "Time Series"
        verbose_name_plural = "Time Series"
        ordering = ("hidden",)

    @property
    def start_date(self):
        try:
            return self.timeseriesrecord_set.earliest().timestamp.astimezone(
                self.time_zone.as_tzinfo
            )
        except TimeseriesRecord.DoesNotExist:
            return None

    @property
    def end_date(self):
        try:
            return self.timeseriesrecord_set.latest().timestamp.astimezone(
                self.time_zone.as_tzinfo
            )
        except TimeseriesRecord.DoesNotExist:
            return None

    @property
    def start_date_naive(self):
        try:
            return (
                self.timeseriesrecord_set.earliest()
                .timestamp.astimezone(self.time_zone.as_tzinfo)
                .replace(tzinfo=None)
            )
        except TimeseriesRecord.DoesNotExist:
            return None

    @property
    def end_date_naive(self):
        try:
            return (
                self.timeseriesrecord_set.latest()
                .timestamp.astimezone(self.time_zone.as_tzinfo)
                .replace(tzinfo=None)
            )
        except TimeseriesRecord.DoesNotExist:
            return None

    def _set_extra_timeseries_properties(self, ahtimeseries):
        if self.gentity.geom:
            location = {
                "abscissa": self.gentity.gpoint.original_abscissa(),
                "ordinate": self.gentity.gpoint.original_ordinate(),
                "srid": self.gentity.gpoint.original_srid,
                "altitude": self.gentity.gpoint.altitude,
            }
        else:
            location = None
        ahtimeseries.time_step = self.time_step
        ahtimeseries.unit = self.unit_of_measurement.symbol
        ahtimeseries.title = self.name
        sign = -1 if self.time_zone.utc_offset < 0 else 1
        ahtimeseries.timezone = "{} (UTC{:+03d}{:02d})".format(
            self.time_zone.code,
            abs(self.time_zone.utc_offset) // 60 * sign,
            abs(self.time_zone.utc_offset) % 60,
        )
        ahtimeseries.variable = self.variable_type.descr
        ahtimeseries.precision = self.precision
        ahtimeseries.location = location
        ahtimeseries.comment = "%s\n\n%s" % (self.gentity.name, self.remarks)

    def get_data(self, start_date=None, end_date=None):
        data = cache.get_or_set(f"timeseries_data_{self.id}", self._get_all_data_as_pd)
        if start_date:
            start_date = start_date.astimezone(self.time_zone.as_tzinfo)
            start_date = start_date.replace(tzinfo=None)
        if end_date:
            end_date = end_date.astimezone(self.time_zone.as_tzinfo)
            end_date = end_date.replace(tzinfo=None)
        data = data.loc[start_date:end_date]
        result = HTimeseries(data)
        self._set_extra_timeseries_properties(result)
        return result

    def _get_all_data_as_pd(self):
        tzinfo = self.time_zone.as_tzinfo
        data = {"value": [], "flags": []}
        index = []
        for record in self.timeseriesrecord_set.all().order_by("timestamp"):
            timestamp = record.timestamp.astimezone(tzinfo).replace(tzinfo=None)
            index.append(timestamp)
            data["value"].append(record.value)
            data["flags"].append(record.flags)
        result = pd.DataFrame(data=data, columns=["value", "flags"], index=index)
        result.index.name = "date"
        return result

    def set_data(self, data):
        ahtimeseries = self._get_htimeseries_from_data(data)
        self.timeseriesrecord_set.all().delete()
        return TimeseriesRecord.bulk_insert(self, ahtimeseries)

    def append_data(self, data):
        ahtimeseries = self._get_htimeseries_from_data(data)
        self._check_new_data_is_newer(ahtimeseries)
        return TimeseriesRecord.bulk_insert(self, ahtimeseries)

    def _check_new_data_is_newer(self, ahtimeseries):
        if not len(ahtimeseries.data):
            return 0
        new_data_start_date = ahtimeseries.data.index[0]
        if self.end_date is not None and self.end_date_naive >= new_data_start_date:
            raise IntegrityError(
                (
                    "Cannot append time series: "
                    "its first record ({}) has a date earlier than the last "
                    "record ({}) of the timeseries to append to."
                ).format(new_data_start_date, self.end_date_naive)
            )

    def _get_htimeseries_from_data(self, data):
        if isinstance(data, HTimeseries):
            return data
        else:
            return HTimeseries(data)

    def get_last_record_as_string(self):
        try:
            return str(self.timeseriesrecord_set.latest())
        except TimeseriesRecord.DoesNotExist:
            return ""

    @property
    def related_station(self):
        try:
            return Station.objects.get(id=self.gentity.id)
        except Station.DoesNotExist:
            return None

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        check_time_step(self.time_step)
        super(Timeseries, self).save(force_insert, force_update, *args, **kwargs)
        cache.delete(f"timeseries_data_{self.id}")


class TimeseriesRecord(models.Model):
    # Ugly primary key hack.
    # Django does not allow composite primary keys, whereas timescaledb can't work
    # without them. Our composite primary key in this case is (timeseries, timestamp).
    # What we do is set managed=False, so that Django won't create the table itself;
    # we create it with migrations.RunSQL(). We also set "primary_key=True" in one of
    # the fields. While technically this is wrong, it fools Django into not expecting
    # an "id" field to exist, and it doesn't affect querying functionality.
    timeseries = models.ForeignKey(Timeseries, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(primary_key=True)
    value = models.FloatField(blank=True, null=True)
    flags = models.CharField(max_length=237, blank=True)

    class Meta:
        managed = False
        get_latest_by = "timestamp"

    @classmethod
    def bulk_insert(cls, timeseries, htimeseries):
        tzinfo = timeseries.time_zone.as_tzinfo
        record_generator = (
            TimeseriesRecord(
                timeseries_id=timeseries.id,
                timestamp=t.Index.to_pydatetime().replace(tzinfo=tzinfo),
                value=t.value,
                flags=t.flags,
            )
            for t in htimeseries.data.itertuples()
        )
        batch_size = 1000
        count = 0
        while True:
            batch = list(islice(record_generator, batch_size))
            if not batch:
                break
            cls.objects.bulk_create(batch, batch_size)
            count += len(batch)
        return count

    def __str__(self):
        tzinfo = self.timeseries.time_zone.as_tzinfo
        precision = self.timeseries.precision
        datestr = self.timestamp.astimezone(tzinfo).strftime("%Y-%m-%d %H:%M")
        return f"{datestr},{self.value:.{precision}f},{self.flags}"


class UserProfile(models.Model):
    """Unused model for backwards compatibility.

    This model isn't being used. We need it so that Enhydris 3 and Enhydris 2.2 can
    co-exist, using the same database. This is because, for some time, Enhydris 2.2
    will be in production but Enhydris 3 will be running on the same database being
    tested. When production is switched to use Enhydris 3 and 2.2 is pronounced dead,
    this model should be removed.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, verbose_name=_("Username")
    )
    fname = models.CharField(_("First Name"), null=True, blank=True, max_length=30)
    lname = models.CharField(_("Last Name"), null=True, blank=True, max_length=30)
    address = models.CharField(_("Location"), null=True, blank=True, max_length=100)
    organization = models.CharField(
        _("Organization"), null=True, blank=True, max_length=100
    )
    email_is_public = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
