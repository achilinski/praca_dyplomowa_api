from rest_framework import serializers
from .models import GpsPoint

class GpsPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = GpsPoint
        fields = ['lat', 'long', 'qr_code', 'name']
