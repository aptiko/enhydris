import csv
from io import BytesIO, StringIO
from zipfile import ZIP_DEFLATED, ZipFile

_station_list_csv_headers = [
    "id",
    "Name",
    "Short name",
    "Type",
    "Owner",
    "Start date",
    "End date",
    "Abscissa",
    "Ordinate",
    "SRID",
    "Altitude",
    "SRID",
    "Automatic",
    "Remarks",
    "Last modified",
]


def _station_csv(s):
    return [
        s.id,
        s.name,
        s.code,
        s.owner,
        s.start_date,
        s.end_date,
        s.original_abscissa(),
        s.original_ordinate(),
        s.original_srid,
        s.altitude,
        s.is_automatic,
        s.remarks,
        s.last_modified,
    ]


_timeseries_list_csv_headers = [
    "id",
    "Station",
    "Variable type",
    "Unit",
    "Name",
    "Precision",
    "Time zone",
    "Time step",
    "Remarks",
]


def _timeseries_csv(t):
    return [
        t.id,
        t.gentity.id,
        t.variable_type.descr if t.variable_type else "",
        t.unit_of_measurement.symbol,
        t.name,
        t.precision,
        t.time_zone.code,
        t.time_step,
    ]


def prepare_csv(queryset):
    with BytesIO() as result:
        with ZipFile(result, "w", ZIP_DEFLATED) as zipfile:
            with StringIO() as stations_csv:
                csvwriter = csv.writer(stations_csv)
                csvwriter.writerow(_station_list_csv_headers)
                for station in queryset:
                    csvwriter.writerow(_station_csv(station))
                zipfile.writestr("stations.csv", stations_csv.getvalue())

            with StringIO() as timeseries_csv:
                csvwriter = csv.writer(timeseries_csv)
                csvwriter.writerow(_timeseries_list_csv_headers)
                for station in queryset:
                    for timeseries in station.timeseries.order_by("variable_type__id"):
                        csvwriter.writerow(_timeseries_csv(timeseries))
                zipfile.writestr("timeseries.csv", timeseries_csv.getvalue())

        return result.getvalue()
