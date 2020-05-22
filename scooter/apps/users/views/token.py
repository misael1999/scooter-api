# Django rest framework
from rest_framework_simplejwt.views import TokenObtainPairView
# Serializers
from scooter.apps.users.serializers.token import (CustomerTokenObtainPairSerializer,
                                                  StationTokenObtainPairSerializer,
                                                  DeliveryManTokenObtainPairSerializer)


class CustomerTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomerTokenObtainPairSerializer


class StationTokenObtainPairView(TokenObtainPairView):
    serializer_class = StationTokenObtainPairSerializer


class DeliveryManTokenObtainPairView(TokenObtainPairView):
    serializer_class = DeliveryManTokenObtainPairSerializer
