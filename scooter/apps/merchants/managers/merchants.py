from django.db.models import Manager


class MerchantManager(Manager):

    def get_queryset(self):
        return super(MerchantManager, self).get_queryset().select_related(
            'delivery_rules',
        )
