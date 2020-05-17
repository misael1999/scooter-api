# Django rest
from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
# Permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from scooter.users.permissions import IsAccountOwner
# Utilities
from scooter.utils.viewsets import ScooterViewSet
# Models
from scooter.users.models.customers import Customer
# Serializers
from scooter.users.serializers.customers import (CustomerSignUpSerializer,
                                                 CustomerSimpleModelSerializer,
                                                 CustomerUserModelSerializer)
from scooter.users.serializers.users import UserModelSimpleSerializer


class CustomerViewSet(ScooterViewSet, mixins.RetrieveModelMixin,
                      mixins.CreateModelMixin, mixins.ListModelMixin,
                      mixins.UpdateModelMixin):
    """ Handle signup and update of merchant """
    queryset = Customer.objects.filter(status=1)
    serializer_class = CustomerUserModelSerializer
    lookup_field = 'id'

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == 'create':
            serializer_class = CustomerSignUpSerializer
        return serializer_class

    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [AllowAny]
        elif self.action in ['partial_update', 'update']:
            permission_classes = [IsAuthenticated, IsAccountOwner]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        """ Customer sign up """
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        customer = serializer.save()
        message = 'Gracias por registrarte, tienes hasta el {time} para verificar tu cuenta'\
            .format(time=str(customer.user.verification_deadline))
        data = self.set_response(status='ok',
                                 data=CustomerUserModelSerializer(customer).data,
                                 message=message)
        return Response(data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        try:
            client = self.get_object()
            partial = request.method == 'PATCH'
            serializer = CustomerSimpleModelSerializer(client, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            data = CustomerUserModelSerializer(client).data
        except Customer.DoesNotExist:
            raise Response(self.set_error_response(status=False, field='Detail', message='El usuario no es un clente'))
        return Response(self.set_response(status='ok', data=data, message='Perfil actualizado correctamente'))
