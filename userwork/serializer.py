from rest_framework import serializers

from gps.serializer import GpsPointSerializer
from .models import PlannedShift, Shift

class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = '__all__'


class PlannedShiftSerializer(serializers.ModelSerializer):
    points = GpsPointSerializer(many=True)  # Nested serialization for points

    class Meta:
        model = PlannedShift
        fields = ['id', 'username', 'start_time', 'end_time', 'truck', 'was_active', 'points']