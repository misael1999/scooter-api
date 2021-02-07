from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
# Models
from scooter.apps.merchants.models import Product
# django
from django.http import Http404, JsonResponse


class AddProductMixin(viewsets.GenericViewSet):
    """Add product mixin

    Manages adding a product object to views
    that require it.
    """
    product = None

    def dispatch(self, request, *args, **kwargs):
        """Verify that the product exists."""
        pk = kwargs['product_id']
        try:
            self.product = get_object_or_404(Product, id=pk)
        except Http404:
            error = {'field': 'detail', 'message': 'No se encontro el comercio'}
            return JsonResponse(data={'errors': error, 'status': 'false'}, status=status.HTTP_404_NOT_FOUND)
        return super(AddProductMixin, self).dispatch(request, *args, **kwargs)

    def get_serializer_context(self):
        """ Add product to serializer context """
        context = super(AddProductMixin, self).get_serializer_context()
        context['product'] = self.product
        return context
