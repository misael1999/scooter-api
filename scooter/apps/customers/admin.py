from django.contrib import admin
# models
from scooter.apps.customers.models import Customer


@admin.register(Customer)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'birthdate', 'phone_number', 'reputation')
    search_fields = ('name', 'last_name', 'phone_number')

