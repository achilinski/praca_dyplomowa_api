import base64
import qrcode
from io import BytesIO
from django.http import HttpResponse
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Truck
from .serializers import TruckSerializer
import hashlib
import os
import uuid

def generate_name_hash(name: str) -> str:
    unique_id = uuid.uuid4()
    name_bytes = (name + str(unique_id)).encode('utf-8')
    sha256_hash = hashlib.sha256()
    sha256_hash.update(name_bytes)
    hash_bytes = sha256_hash.digest()
    hash_base64 = base64.b64encode(hash_bytes).decode('utf-8')
    
    return str(hash_base64[:10])

@api_view(['POST'])
def create_truck(request):
    mialge = request.data.get('milage',0)
    #qr_code = request.data.get('qr_code')
    name = request.data.get('name')
    if type(name) != str:
        name = str(name)
    if not qr_code:
        qr_code = f"{generate_name_hash(name + str(Truck.objects.count() + 1))}"

    if not name:
        name = f"truck_{Truck.objects.count() + 1}"

    truck = Truck.objects.create(name=name, milage=mialge, qr_code=qr_code)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    qr.add_data(truck.qr_code)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img_bytes = BytesIO()
    img.save(img_bytes)

    media_path = "media"
    if not os.path.exists(media_path):
        os.makedirs(media_path)
    
    img.save(os.path.join(media_path, f"{truck.qr_code}.png"))
    img_bytes.seek(0)

    return HttpResponse(img_bytes, content_type="image/png")

@api_view(['GET'])
def get_truck_by_qr(request):
    qr_code = request.data.get('qr_code')
    try:
        truck = Truck.objects.get(qr_code=qr_code)
    except Truck.DoesNotExist:
        return Response({"error":"Truck not found"},status=status.HTTP_404_NOT_FOUND)
    
    serializer = TruckSerializer(truck)
    return Response(serializer.data)

@api_view(['GET'])
def get_all_trucks(request):
    trucks = Truck.objects.all()
    serializer = TruckSerializer(trucks, many=True)
    return Response(serializer.data)


# Create your views here.
