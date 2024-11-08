import base64
from datetime import datetime
import hashlib
import uuid
import qrcode
from io import BytesIO
from django.http import HttpResponse
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
import decimal


from trucks.models import Truck 
from datetime import datetime, timezone

from .models import GpsPoint

def generate_name_hash(name: str) -> str:
    unique_id = uuid.uuid4()
    name_bytes = (name + str(unique_id)).encode('utf-8')
    sha256_hash = hashlib.sha256()
    sha256_hash.update(name_bytes)
    hash_bytes = sha256_hash.digest()
    hash_base64 = base64.b64encode(hash_bytes).decode('utf-8')
    
    return str(hash_base64[:10])

@api_view(['POST'])
def create_gps_point(request):
    lat = request.data.get('lat')
    long = request.data.get('long')
    name = request.data.get('name', None)

    if lat:
        lat = float(lat)
        lat = decimal.Decimal(lat)
    if long:
        long = float(long)
        long = decimal.Decimal(long)
    if type(name) != str:
        name = str(name)
    if name:
        qr_code = generate_name_hash(name)
    else:
        name = GpsPoint.objects.count()
        qr_code = generate_name_hash(f'{name + 1}')
    
    try:
        point = GpsPoint.objects.create(lat = lat, long = long, qr_code = qr_code, name = name)
    except Exception as e:
        return Response({str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({"succes":"Point created"},status=status.HTTP_201_CREATED) 


@api_view(['POST'])
def get_gps_point_by_name(request):
    name = request.data.get('name')

    try:
        point = GpsPoint.objects.get(name = name)
    except GpsPoint.DoesNotExist:
        return Response({"error":"Object does not exist"},status=status.HTTP_404_NOT_FOUND)
    
    return Response({point.lat, point.long}, status=status.HTTP_200_OK)

@api_view(['POST'])
def get_gps_point_by_qr(request):
    name = request.data.get('qr_code')

    try:
        point = GpsPoint.objects.get(name = name)
    except GpsPoint.DoesNotExist:
        return Response({"error":"Object does not exist"},status=status.HTTP_404_NOT_FOUND)
    
    return Response({point.lat, point.long}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_all_gps_points(request):
    try:
        points = GpsPoint.objects.all()
    except GpsPoint.DoesNotExist:
        return Response({"error":"Object does not exist"},status=status.HTTP_404_NOT_FOUND)

    points_data = []
    for point in points:
        points_data.append({
            'lat': point.lat,
            'long': point.long,
            'qr_code': point.qr_code,
            'name': point.name
        })
    return Response({"points": points_data}, status=status.HTTP_200_OK)

    



