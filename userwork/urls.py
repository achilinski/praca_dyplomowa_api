from django.urls import path
from . import views

urlpatterns = [
    path('start/', views.register_start_work, name='register_start_work'),
    path('end/', views.register_end_work, name='register_end_work'),
    path('shifts/', views.get_shifts, name='get_shifts'),
    path('all/', views.get_all_shifts, name='get_all_shifts'),
    path('working/', views.is_still_working, name='is_still_working'),
]
