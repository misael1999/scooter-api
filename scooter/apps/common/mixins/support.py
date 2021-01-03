from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
# Models
from scooter.apps.support.models import Support
# django
from django.http import Http404, JsonResponse


class AddSupportMixin(viewsets.GenericViewSet):
    """Add support mixin

    Manages adding a support object to views
    that require it.
    """
    support = None

    def dispatch(self, request, *args, **kwargs):
        """Verify that the support exists."""
        pk = kwargs['support_id']
        try:
            self.support = get_object_or_404(Support, id=pk)
        except Http404:
            error = {'field': 'detail', 'message': 'No se encontro el cliente'}
            return JsonResponse(data={'errors': error, 'status': 'false'}, status=status.HTTP_404_NOT_FOUND)
        return super(AddSupportMixin, self).dispatch(request, *args, **kwargs)

    def get_serializer_context(self):
        """ Add support to serializer context """
        context = super(AddSupportMixin, self).get_serializer_context()
        context['support'] = self.support
        return context
