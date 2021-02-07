from django.db.models import Manager


class MerchantPromotionManager(Manager):

    def get_queryset(self):
        return super(MerchantPromotionManager, self).get_queryset().select_related(
            'rule'
        ).prefetch_related(
            'time_intervals'
        )


class MerchantPromotionTimeIntervalManager(Manager):
    def get_queryset(self):
        return super(MerchantPromotionTimeIntervalManager, self).get_queryset()\
            .prefetch_related(
            'schedules'
            )
