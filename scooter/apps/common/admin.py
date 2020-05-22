from django.contrib import admin
# models
from scooter.apps.common.models.status import Status


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    """ Status model """
    list_display = ('id', 'name', 'slug_name')
    search_fields = ('name', 'slug_name')