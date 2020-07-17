""" Order rating model."""
# Django
from django.db import models

# Utilities
from scooter.utils.models import ScooterModel


class RatingOrder(ScooterModel):
    """ Order rating.
        Rate order when is finished
    """

    order = models.OneToOneField(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='rated_order'
    )
    station = models.ForeignKey('stations.Station', on_delete=models.CASCADE)

    user = models.ForeignKey('users.User', on_delete=models.CASCADE)

    delivery_man = models.ForeignKey('delivery_men.DeliveryMan', on_delete=models.CASCADE)

    rating_customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.SET_NULL,
        null=True,
        help_text='Customer that emits the rating',
        related_name='rating_customer',
    )

    comments = models.TextField(blank=True, null=True)

    rating = models.IntegerField(default=1)

    def __str__(self):
        """Return summary."""
        return self.order
