""" FAQ models """
from django.db import models
# Utilities
from scooter.utils.models.scooter import ScooterModel


class Question(ScooterModel):

    title = models.CharField(max_length=200, unique=True)
    answer = models.TextField()

    def __str__(self):
        return self.title
