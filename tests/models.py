from django.db import models
from dj_bitfields import BitStringField
from bitstring import Bits


class TestFieldModel(models.Model):
    name = models.CharField(max_length=256)
    schedule = BitStringField(max_length=8,default=None)

    class Meta:
        app_label='tests'
