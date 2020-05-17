from django.contrib import admin
# models
from ecommerceteh.common.models.status import Status, PurchaseStatus, ProductStatus
from ecommerceteh.common.models.products import (ProductCondition, DeliveryTime,
                                                 ShippingForm, Color, DeliveryWay,
                                                 PaymentType)
from ecommerceteh.common.models.promotions import TypeAmount


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    """ Status model """
    list_display = ('id', 'name', 'slug_name')
    search_fields = ('name', 'slug_name')