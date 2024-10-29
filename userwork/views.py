import base64
from datetime import datetime
import qrcode
from io import BytesIO
from django.http import HttpResponse
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializer import ShiftSerializer
from .models import Shift
import hashlib
from trucks.models import Truck 

# Create your views here.

@api_view(['POST'])
def register_start_work(request):
    username = request.data.get('username')
    truck_qr = request.data.get('qr_code')
    print("-----------------")
    print(username)
    print(truck_qr)
    try:
        truck = Truck.objects.get(qr_code=truck_qr)
    except truck.DoesNotExist:
        return Response({"error":"Truck not found"},status=status.HTTP_404_NOT_FOUND)

    shift = Shift.objects.create(username=username, truck=truck, start_time=datetime.now())

    return Response({"success":"Shift started"},status=status.HTTP_201_CREATED)
    
@api_view(['POST'])
def register_end_work(request):
    username = request.data.get('username')
    truck_qr = request.data.get('qr_code')

    try:
        truck = Truck.objects.get(qr_code=truck_qr)
        print(truck)
    except Truck.DoesNotExist:
        return Response({"error":"Truck not found"},status=status.HTTP_404_NOT_FOUND)

    try:
        print(Shift.objects.filter(end_time=None))
        shift = Shift.objects.filter(username=username, truck=truck, end_time=None)
        print(shift)
        print(shift.count())   
        if(shift.count() > 1):
            for s in shift:
                s.end_time = datetime.now()
                s.save()
            return Response({"success":"Shift ended"},status=status.HTTP_200_OK)
        else:
            shift = Shift.objects.get(username=username, truck=truck, end_time=None)
            
    except Shift.DoesNotExist:
        return Response({"error":"Shift not found"},status=status.HTTP_404_NOT_FOUND)
    
    if shift.truck != truck:
        return Response({"error":"Truck does not match"},status=status.HTTP_400_BAD_REQUEST)

    shift.end_time = datetime.now()
    shift.save()

    return Response({"success":"Shift ended"},status=status.HTTP_200_OK)

@api_view(['POST'])
def get_shifts(request):
    username = request.data.get('username')
    print(username)
    shifts = Shift.objects.filter(username=username)
    shift_data = []
    for shift in shifts:
        shift_data.append({
            'username': shift.username,
            'truck_qr': shift.truck.qr_code,
            'start_time': shift.start_time,
            'end_time': shift.end_time
        })
    return Response({"shifts": shift_data}, status=status.HTTP_200_OK)

@api_view(['POST'])
def is_still_working(request):
    username = request.data.get('username')
    try:
        shifts = Shift.objects.get(username=username, end_time=None)
    except Shift.DoesNotExist:
        return Response({"is_working": False}, status=status.HTTP_200_OK)
    if shifts:
        return Response({"is_working": True}, status=status.HTTP_200_OK)
    return Response({"is_working": False}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_all_shifts(request):
    shifts = Shift.objects.all()
    shift_data = []
    for shift in shifts:
        shift_data.append({
            'username': shift.username,
            'truck_qr': shift.truck.qr_code,
            'start_time': shift.start_time,
            'end_time': shift.end_time
        })
    return Response({"shifts": shift_data}, status=status.HTTP_200_OK)

