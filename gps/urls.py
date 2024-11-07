from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_gps_point, name='create_gps_point'),
    path('get-name/', view=views.get_gps_point_by_name, name='get_gps_point_by_name'),
    path('get-qr/', view=views.get_gps_point_by_qr, name='get_gps_point_by_qr'),
    path('get-all/', view=views.get_all_gps_points, name='get_all_gps_points'),

]
