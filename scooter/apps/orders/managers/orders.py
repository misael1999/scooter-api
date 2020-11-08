from django.db.models import Manager


class OrderManager(Manager):

    def get_queryset(self):
        return super(OrderManager, self).get_queryset().select_related(
            'merchant',
        )
