""" Clients URLs module."""
from django.urls import path, include
# Django rest frameworks
from rest_framework.routers import DefaultRouter
# Views
from scooter.apps.payments import views

router = DefaultRouter()
router.register(r'api/v1/customers/(?P<customer_id>[a-zA-Z0-9_-]+)/cards',
                views.CardsViewSet, basename='customers_cards')
urlpatterns = [
    # Users
    path('', include(router.urls))
]
