"""
URL configuration for testapi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))"gps_gpspoint"gps_shiftgpspointset_point_setgps_shiftgpspointset
"""
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view as swagger_get_schema_view
from django.conf import settings
from django.conf.urls.static import static

schema_view = swagger_get_schema_view(
    openapi.Info(
        title="Praca inynierska API",
        default_version="1.0.0",
        description="API"
    ),
    public=True
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/truck/', include('trucks.urls')),
    path('api/shift/', include('userwork.urls')),
    path('api/gps/', include('gps.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name="swagger-schema"),
    path('admin_panel/', include('admin_panel.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
