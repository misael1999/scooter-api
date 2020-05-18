# Django rest framework
from rest_framework_simplejwt.views import TokenObtainPairView
# Serializers
from scooter.users.serializers import (CustomerTokenObtainPairSerializer,
                                       StationTokenObtainPairSerializer)


class CustomerTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomerTokenObtainPairSerializer


class StationTokenObtainPairView(TokenObtainPairView):
    serializer_class = StationTokenObtainPairSerializer

