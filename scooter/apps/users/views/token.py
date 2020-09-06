# Django rest framework
from rest_framework import status
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
# Serializers
from scooter.apps.users.serializers.token import (CustomerTokenObtainPairSerializer,
                                                  StationTokenObtainPairSerializer,
                                                  DeliveryManTokenObtainPairSerializer,
                                                  MerchantTokenObtainPairSerializer,
                                                  CustomerFacebookAuthSerializer, CustomerAppleAuthSerializer,
                                                  MarketerTokenObtainPairSerializer)
import json
# Views
from scooter.utils.viewsets.scooter import ScooterViewSet


class CustomerTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomerTokenObtainPairSerializer


class StationTokenObtainPairView(TokenObtainPairView):
    serializer_class = StationTokenObtainPairSerializer


class DeliveryManTokenObtainPairView(TokenObtainPairView):
    serializer_class = DeliveryManTokenObtainPairSerializer


class MerchantManTokenObtainPairView(TokenObtainPairView):
    serializer_class = MerchantTokenObtainPairSerializer


class MarketingTokenObtainPairView(TokenObtainPairView):
    serializer_class = MarketerTokenObtainPairSerializer


class CustomerFacebookAuthViewSet(ScooterViewSet, CreateModelMixin):
    serializer_class = CustomerFacebookAuthSerializer

    def create(self, request, *args, **kwargs):
        """ Customer sign up """
        serializer = CustomerFacebookAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        access = serializer.save()
        message = 'Se ha autenticado con facebook correctamnente'
        return Response(access, status=status.HTTP_201_CREATED)


class CustomerAppleAuthViewSet(ScooterViewSet, CreateModelMixin):

    def create(self, request, *args, **kwargs):
        """ Customer sign up """
        serializer = CustomerAppleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        access = serializer.save()
        message = 'Se ha autenticado con apple correctamnente'
        return Response(access, status=status.HTTP_201_CREATED)

