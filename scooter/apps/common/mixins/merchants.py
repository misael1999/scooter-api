from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
# Models
from scooter.apps.merchants.models import Merchant
# django
from django.http import Http404, JsonResponse


class AddMerchantMixin(viewsets.GenericViewSet):
    """Add merchant mixin

    Manages adding a merchant object to views
    that require it.
    """
    merchant = None

    def dispatch(self, request, *args, **kwargs):
        """Verify that the merchant exists."""
        pk = kwargs['merchant_id']
        try:
            self.merchant = get_object_or_404(Merchant, id=pk)
        except Http404:
            error = {'field': 'detail', 'message': 'No se encontro el comercio'}
            return JsonResponse(data={'errors': error, 'status': 'false'}, status=status.HTTP_404_NOT_FOUND)
        return super(AddMerchantMixin, self).dispatch(request, *args, **kwargs)

    def get_serializer_context(self):
        """ Add merchant to serializer context """
        context = super(AddMerchantMixin, self).get_serializer_context()
        context['merchant'] = self.merchant
        return context
