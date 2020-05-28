from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
# Models
from scooter.apps.delivery_men.models import DeliveryMan
# django
from django.http import Http404, JsonResponse


class AddDeliveryManMixin(viewsets.GenericViewSet):
    """Add delivery_man mixin

    Manages adding a delivery_man object to views
    that require it.
    """
    delivery_man = None

    def dispatch(self, request, *args, **kwargs):
        """Verify that the delivery_man exists."""
        pk = kwargs['delivery_man_id']
        try:
            self.delivery_man = get_object_or_404(DeliveryMan, id=pk)
        except Http404:
            error = {'field': 'detail', 'message': 'No se encontro el repartidor'}
            return JsonResponse(data={'errors': error, 'status': 'false'}, status=status.HTTP_404_NOT_FOUND)
        return super(AddDeliveryManMixin, self).dispatch(request, *args, **kwargs)

    def get_serializer_context(self):
        """ Add delivery_man to serializer context """
        context = super(AddDeliveryManMixin, self).get_serializer_context()
        context['delivery_man'] = self.delivery_man
        return context
