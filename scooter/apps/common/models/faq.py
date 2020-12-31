""" FAQ models """
from django.db import models
# Utilities
from scooter.utils.models.scooter import ScooterModel


class GroupQuestion(ScooterModel):

    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Question(ScooterModel):

    title = models.CharField(max_length=200, unique=True)
    answer = models.TextField()
    group = models.ForeignKey(GroupQuestion, on_delete=models.DO_NOTHING, related_name="questions", null=True)

    def __str__(self):
        return self.title
