from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
# Models
from scooter.apps.customers.models import Customer
# django
from django.http import Http404, JsonResponse


class AddCustomerMixin(viewsets.GenericViewSet):
    """Add customer mixin

    Manages adding a customer object to views
    that require it.
    """
    customer = None

    def dispatch(self, request, *args, **kwargs):
        """Verify that the customer exists."""
        pk = kwargs['customer_id']
        try:
            self.customer = get_object_or_404(Customer, id=pk)
        except Http404:
            error = {'field': 'detail', 'message': 'No se encontro el cliente'}
            return JsonResponse(data={'errors': error, 'status': 'false'}, status=status.HTTP_404_NOT_FOUND)
        return super(AddCustomerMixin, self).dispatch(request, *args, **kwargs)

    def get_serializer_context(self):
        """ Add customer to serializer context """
        context = super(AddCustomerMixin, self).get_serializer_context()
        context['customer'] = self.customer
        return context
