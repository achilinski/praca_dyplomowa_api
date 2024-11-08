from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_truck, name='create_truck'),
    path('get-qr/', views.get_truck_by_qr, name='get_truck_by_qr'),
    path('all/', views.get_all_trucks, name='get_all_trucks'),
]
