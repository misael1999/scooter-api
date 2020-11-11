from django.db.models import Manager


class DeliveryManManager(Manager):

    def get_queryset(self):
        return super(DeliveryManManager, self).get_queryset().select_related(
            'status',
            'delivery_status'
        )
