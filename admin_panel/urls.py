from django.urls import path
from .views import user_stats_view, truck_stats_view, user_shifts_view, create_gps_point_view, create_truck_view, view_truck_qr_codes

urlpatterns = [
    path('user_shifts/<str:username>/', user_shifts_view, name='user_shifts'),
    path('create_gps_point/', create_gps_point_view, name='create_gps_point'),
    path('create_truck/', create_truck_view, name='create_truck'),
    path('view_truck_qr_codes/', view_truck_qr_codes, name='view_truck_qr_codes'),
    path('user_stats/', user_stats_view, name='user_stats'),
    path('truck_stats/', truck_stats_view, name='truck_stats'),
]
