from django.contrib import admin
# models
from scooter.apps.common.models.status import Status
from scooter.apps.common.models.common import TypeAddress
from scooter.apps.common.models.orders import OrderStatus


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    """ Status model """
    list_display = ('id', 'name', 'slug_name')
    search_fields = ('name', 'slug_name')


@admin.register(TypeAddress)
class TypeAddressAdmin(admin.ModelAdmin):
    """ Type address model """
    list_display = ('id', 'name', 'slug_name')
    search_fields = ('name', 'slug_name')


@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    """ Order status model """
    list_display = ('id', 'name', 'slug_name', 'type_service')
    search_fields = ('name', 'slug_name')
