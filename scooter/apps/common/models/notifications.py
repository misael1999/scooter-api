""" Notifications models """
from django.db import models
# Utilities
from scooter.utils.models.scooter import ScooterModel


class TypeNotification(ScooterModel):
    name = models.CharField(max_length=30)
    slug_name = models.CharField(max_length=30)

    def __str__(self):
        return self.slug_name


class Notification(ScooterModel):
    title = models.CharField(max_length=50)
    body = models.CharField(max_length=100)
    action = models.CharField(max_length=30, blank=True, null=True)
    payload = models.CharField(max_length=30, blank=True, null=True)
    type_notification = models.ForeignKey(TypeNotification, on_delete=models.DO_NOTHING)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='notifications')

    def __str__(self):
        return self.title
