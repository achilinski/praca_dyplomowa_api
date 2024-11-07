import base64
from datetime import datetime
import qrcode
from io import BytesIO
from django.http import HttpResponse
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializer import ShiftSerializer
from .models import Break, Shift
import hashlib
from trucks.models import Truck 
from datetime import datetime, timezone

now = datetime.now(timezone.utc)

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

@api_view(['POST'])
def gat_user_total_work_time(request):
    username = request.data.get('username')
    shifts = Shift.objects.filter(username=username)
    datenow = datetime.now(timezone.utc)
    total_time = datenow - datenow
    for shift in shifts:
        if shift.end_time is None:
            total_time += datetime.now(timezone.utc) - shift.start_time
        else:
            total_time += shift.end_time - shift.start_time
    if total_time.total_seconds() < 0:
        total_time = datetime.now(timezone.utc) - datetime.now(timezone.utc)
    return Response({total_time.total_seconds()}, status=status.HTTP_200_OK)

@api_view(['POST'])
def get_user_month_work_time(request):
    username = request.data.get('username')
    shifts = Shift.objects.filter(username=username, start_time__month=datetime.now(timezone.utc).month)
    datenow = datetime.now(timezone.utc)
    total_time = datenow - datenow
    for shift in shifts:
        if shift.start_time.month == datetime.now().month:
            if shift.end_time is None:
                total_time += datetime.now(timezone.utc) - shift.start_time
            else:
                total_time += shift.end_time - shift.start_time
    print(total_time)
    if total_time.total_seconds() <= 0:
        total_time = 0
    return Response({total_time.total_seconds()}, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_user_today_work_time(request):
    username = request.data.get('username')
    shifts = Shift.objects.filter(username=username, start_time__date=datetime.now(timezone.utc).date())
    if not shifts.exists():
        return Response({'0'},status=status.HTTP_200_OK)
    datenow = datetime.now(timezone.utc)
    total_time = datenow - datenow
    for shift in shifts:
        if shift.start_time.month == datetime.now().today:
            if shift.end_time is None:
                total_time += datetime.now(timezone.utc) - shift.start_time
            else:
                total_time += shift.end_time - shift.start_time
    print(total_time)
    if total_time.total_seconds() < 0:
        total_time = datetime.now(timezone.utc) - datetime.now(timezone.utc)
    return Response({total_time.total_seconds()}, status=status.HTTP_200_OK)

@api_view(['POST'])
def start_break(request):
    username = request.data.get('username')
    try:
        shift = Shift.objects.get(username=username, end_time=None)
    except Shift.DoesNotExist:
        return Response({"error":"Shift not found"},status=status.HTTP_404_NOT_FOUND)
    start_time = datetime.now()
    break_time = Break.objects.create(shift=shift, start_time=start_time)
    return Response({"success":"Break started"},status=status.HTTP_201_CREATED)

@api_view(['POST'])
def stop_break(request):
    username = request.data.get('username')
    try:
        shift = Shift.objects.get(username=username, end_time=None)
    except Shift.DoesNotExist:
        return Response({"error":"Shift not found"},status=status.HTTP_404_NOT_FOUND)
    try:
        break_time = Break.objects.get(shift=shift, end_time=None)
    except Break.DoesNotExist:
        return Response({"error":"Break not found"},status=status.HTTP_404_NOT_FOUND)
    break_time.end_time = datetime.now()
    break_time.save()
    return Response({"success":"Break ended"},status=status.HTTP_200_OK)

@api_view(['POST'])
def is_break(request):
    username = request.data.get('username')
    try:
        shift = Shift.objects.get(username=username, end_time=None)
    except Shift.DoesNotExist:
        return Response({"error":"Shift not found"},status=status.HTTP_404_NOT_FOUND)
    try:
        break_time = Break.objects.get(shift=shift, end_time=None)
    except Break.DoesNotExist:
        return Response({"is_break": False}, status=status.HTTP_200_OK)
    return Response({"is_break":True},status=status.HTTP_200_OK)



