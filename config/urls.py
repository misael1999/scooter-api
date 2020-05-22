"""Main URLs module."""

from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib import admin


urlpatterns = [
    # Django Admin
    path('', include('swagger_ui.urls')),
    path(settings.ADMIN_URL, admin.site.urls),
    #  Apps Urls
    # Users
    path('', include('scooter.users.urls')),
    # Common
    path('', include('scooter.common.urls')),
    # Delivery men
    path('', include('scooter.delivery_men.urls')),
    # Vehicles
    path('', include('scooter.vehicles.urls'))

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
