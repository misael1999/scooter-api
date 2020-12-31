from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from scooter.apps.common.models import Status
from scooter.apps.common.models.faq import Question
from scooter.apps.common.serializers.faq import QuestionModelSerializer, QuestionSimpleSerializer
from scooter.utils.viewsets import ScooterViewSet


class FaqViewSet(ScooterViewSet, mixins.ListModelMixin,
                 mixins.CreateModelMixin, mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin):

    serializer_class = QuestionModelSerializer
    pagination_class = None
    queryset = Question.objects.filter(status=1)
    # Filters
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ('title',)
    # ordering_fields = ('created', 'title')
    # Affect the default order
    ordering = ('id',)

    def get_permissions(self):
        permission_classes = []
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        elif self.action in ['partial_update', 'update', 'create']:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'list':
            return QuestionSimpleSerializer
        return self.serializer_class

    def perform_destroy(self, instance):
        try:
            sts = Status.objects.get(slug_name='deleted')
            instance.status_id = sts
            instance.save()
        except Status.DoesNotExist:
            error = self.set_error_response(status=False, field='status',
                                            message='Ha ocurrido un error al borrar la pregunta')
            return Response(data=error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
