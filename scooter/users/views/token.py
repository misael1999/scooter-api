# Django rest framework
from rest_framework_simplejwt.views import TokenObtainPairView
# Serializers
from scooter.users.serializers import CustomerTokenObtainPairSerializer


class CustomerTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomerTokenObtainPairSerializer

