from rest_framework import serializers

from parler_rest.fields import TranslatedFieldsField
from parler_rest.serializers import TranslatableModelSerializer
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from enhydris import models


class TimeseriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Timeseries
        fields = "__all__"


class LayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Layer
        fields = "__all__"


class GareaListSerializer(serializers.ModelSerializer):
    # To see why we specify the id, check https://stackoverflow.com/questions/36473795/
    id = serializers.IntegerField(required=False)
    detail = serializers.HyperlinkedIdentityField(
        read_only=True, view_name="garea-detail"
    )

    class Meta:
        model = models.Garea
        fields = ("id", "layer", "name", "code", "detail")


class GareaDetailSerializer(GeoFeatureModelSerializer):
    # To see why we specify the id, check https://stackoverflow.com/questions/36473795/
    id = serializers.IntegerField(required=False)

    class Meta:
        model = models.Garea
        geo_field = "geometry"
        fields = ("id", "layer", "name", "code", "remarks")


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Organization
        fields = "__all__"


class PersonSerializer(serializers.ModelSerializer):
    # To see why we specify the id, check https://stackoverflow.com/questions/36473795/
    id = serializers.IntegerField(required=False)

    class Meta:
        model = models.Person
        fields = "__all__"


class TimeZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TimeZone
        fields = "__all__"


class IntervalTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IntervalType
        fields = "__all__"


class FileTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FileType
        fields = "__all__"


class EventTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EventType
        fields = "__all__"


class InstrumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.InstrumentType
        fields = "__all__"


class TimeStepSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=models.TimeStep, required=False)

    class Meta:
        model = models.TimeStep
        fields = "__all__"


class VariableSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=models.Variable, required=False)

    class Meta:
        model = models.Variable
        fields = "__all__"


class UnitOfMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UnitOfMeasurement
        fields = "__all__"


class GentityFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.GentityFile
        fields = "__all__"


class GentityEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.GentityEvent
        fields = "__all__"


class InstrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Instrument
        fields = "__all__"


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Station
        exclude = ("creator", "maintainers")

    def validate_nested_many_serializer(self, value):
        try:
            return [x["id"] for x in value]
        except KeyError as e:
            raise serializers.ValidationError(str(e))

    validate_maintainers = validate_nested_many_serializer
