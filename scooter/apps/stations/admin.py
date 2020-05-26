from django.contrib import admin
# models
from scooter.apps.stations.models import Station


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('id', 'contact_person', 'station_name')
    search_fields = ('contact_person', 'station_name')

