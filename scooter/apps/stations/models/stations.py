# django
from django.contrib.gis.db import models
# Utilities
from scooter.utils.models import ScooterModel


class Station(ScooterModel):
    user = models.OneToOneField('users.User', on_delete=models.DO_NOTHING)
    contact_person = models.CharField(max_length=80)
    picture = models.ImageField(upload_to='stations/pictures/', blank=True, null=True)
    station_name = models.CharField(max_length=100)
    station_verified = models.BooleanField(default=False)
    document_verified = models.FileField(upload_to='stations/documents/')

    # Config
    assign_delivery_manually = models.BooleanField(default=False)
    cancellation_policies = models.TextField(blank=True, null=True)
    allow_cancellations = models.BooleanField(default=True)

    # Help
    information_is_complete = models.BooleanField(default=False)

    # stats
    reputation = models.FloatField(default=0)
    total_orders = models.PositiveIntegerField(default=0)
    total_clients = models.PositiveIntegerField(default=0)
    total_delivery_man = models.PositiveIntegerField(default=0)
    total_messages_support = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.station_name


class StationService(ScooterModel):
    service = models.ForeignKey('common.Service', on_delete=models.DO_NOTHING)
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="services")
    base_rate_price = models.FloatField()
    price_kilometer = models.FloatField()
    from_kilometer = models.FloatField()
    to_kilometer = models.FloatField()

    class Meta:
        unique_together = ('station', 'service')

    def __str__(self):
        return self.service.name


class StationPhoneNumbers(ScooterModel):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    alias = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=15)
    is_default = models.BooleanField(default=False)


class StationSchedule(ScooterModel):
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="schedules")
    schedule = models.ForeignKey('common.Schedule', on_delete=models.DO_NOTHING)
    from_hour = models.TimeField()
    to_hour = models.TimeField()

    class Meta:
        unique_together = ('station', 'schedule')


class StationAddress(ScooterModel):
    station = models.OneToOneField(Station, on_delete=models.CASCADE, related_name="address")
    street = models.CharField(max_length=100)
    suburb = models.CharField(max_length=60)
    postal_code = models.CharField(max_length=10)
    exterior_number = models.CharField(max_length=10)
    inside_number = models.CharField(max_length=10, blank=True, null=True)
    references = models.CharField(max_length=150, blank=True, null=True)
    point = models.PointField(blank=True, null=True)


# For the clients of each station
class MemberStation(ScooterModel):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE)
    total_orders = models.PositiveIntegerField(default=0)
    total_orders_cancelled = models.PositiveIntegerField(default=0)
    first_order_date = models.DateTimeField(auto_now_add=True)
    last_order_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('station', 'customer')
        db_table = 'stations_member_station'

    def __str__(self):
        return self.customer.name








