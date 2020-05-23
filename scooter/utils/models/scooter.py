""" DJANGO UTILITIES """
from django.db import models


class ScooterModel(models.Model):
    """  """
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    status = models.ForeignKey('common.Status', on_delete=models.DO_NOTHING, default=1)

    class Meta:
        abstract = True
        get_latest_by = 'created'
        ordering = ['-created', '-modified']



