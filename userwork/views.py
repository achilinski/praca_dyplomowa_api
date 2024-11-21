import base64
from datetime import datetime
import json
import qrcode
from io import BytesIO
from django.http import HttpResponse
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response

from gps.models import GpsPoint

from .serializer import PlannedShiftSerializer, ShiftSerializer
from .models import Break, PlannedShift, PlannedShiftPoint, Shift
import hashlib
from trucks.models import Truck 
from datetime import datetime, timezone

now = datetime.now(timezone.utc)

# Create your views here.

@api_view(['POST'])
def register_start_work(request):
    username = request.data.get('username')
    truck_qr = request.data.get('truck_qr')
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
    truck_qr = request.data.get('truck_qr')
    
    if truck_qr == None:
        return Response({"error":"Input truck qr code"},status=status.HTTP_404_NOT_FOUND)

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
    if total_time.total_seconds() <= 0:
        return Response({0.0}, status=status.HTTP_200_OK)
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
        return Response({0.0}, status=status.HTTP_200_OK)
    return Response({total_time.total_seconds()}, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_user_today_work_time(request):
    username = request.data.get('username')
    shifts = Shift.objects.filter(username=username, start_time__date=datetime.now(timezone.utc).date())
    if not shifts.exists():
        return Response({0.0},status=status.HTTP_200_OK)
    datenow = datetime.now(timezone.utc)
    total_time = datenow - datenow
    for shift in shifts:
        if shift.end_time is None:
            total_time += datetime.now(timezone.utc) - shift.start_time
        else:
            total_time += shift.end_time - shift.start_time
    total_seconds = total_time.total_seconds()
    print(total_seconds)
    if total_time.total_seconds() < 0:
        return Response({0.0}, status=status.HTTP_200_OK)
    return Response({total_seconds}, status=status.HTTP_200_OK)

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
        break_time = Break.objects.filter(shift=shift, end_time=None)
    except Break.DoesNotExist:
        return Response({"error":"Break not found"},status=status.HTTP_404_NOT_FOUND)
    print(break_time)
    for break_time in break_time:
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
        break_time = Break.objects.filter(shift=shift, end_time=None)
        print(break_time)
    except Break.DoesNotExist:
        return Response({"is_break": False}, status=status.HTTP_200_OK)
    if break_time:
        return Response({"is_break": True}, status=status.HTTP_200_OK)
    else:
        return Response({"is_break": False}, status=status.HTTP_200_OK)




@api_view(['POST'])
def create_planned_shift(request):
    username = request.data.get('username')
    truck_qr = request.data.get('truck_qr')
    points = request.data.get('points')  # Expected to be an ordered list
    start_date = request.data.get('start_date')
    end_date = request.data.get('end_date')

    # Validate required fields
    if not all([username, truck_qr, points, start_date, end_date]):
        return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

    # Parse datetime fields
    try:
        print(start_date)
        print(end_date)
        start_date = datetime.fromisoformat(start_date)
        end_date = datetime.fromisoformat(end_date)
    except ValueError:
        return Response({"error": "Invalid date format. Use ISO 8601 format."}, status=status.HTTP_400_BAD_REQUEST)

    # Retrieve the truck
    try:
        truck = Truck.objects.get(qr_code=truck_qr)
    except Truck.DoesNotExist:
        return Response({"error": "Truck not found."}, status=status.HTTP_404_NOT_FOUND)

    # Create the planned shift
    planned_shift = PlannedShift.objects.create(
        username=username,
        truck=truck,
        start_time=start_date,
        end_time=end_date
    )
    try:
        points = json.loads(points)
    except json.JSONDecodeError as e:
        print(f"Error decoding points: {e}")

    print(points)
    # Add points with order
    for index, point_qr in enumerate(points):
        try:
            gps_point = GpsPoint.objects.get(qr_code=point_qr)
            # Create intermediary model instance with the order
            PlannedShiftPoint.objects.create(
                planned_shift=planned_shift,
                gps_point=gps_point,
                order=index
            )
        except GpsPoint.DoesNotExist:
            planned_shift.delete()
            return Response(
                {"error": f"GPS point with QR code '{point_qr}' not found. Deleting planned shif"},
                status=status.HTTP_404_NOT_FOUND
            )

    return Response({"success": "Planned shift created."}, status=status.HTTP_201_CREATED)

# {
#   "username": "john_doe",
#   "truck_qr": "TRUCK123QR",
#   "points": ["GPS1QR", "GPS2QR", "GPS3QR"],
#   "start_date": "2024-11-25T08:00:00",
#   "end_date": "2024-11-25T17:00:00"
# }

@api_view(['POST'])
def get_user_planned_shifts(request):
    username = request.data.get('username')
    try:
        # Filter planned shifts by the username
        planned_shifts = PlannedShift.objects.filter(username=username).order_by('start_time')

        # If no planned shifts exist, return an appropriate message
        if not planned_shifts.exists():
            return Response(
                {"message": "No planned shifts found for this user."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Serialize the planned shifts
        serializer = PlannedShiftSerializer(planned_shifts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





