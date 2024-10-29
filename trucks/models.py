from django.db import models


class Truck(models.Model):
    name = models.CharField(max_length=100)
    milage = models.IntegerField()
    qr_code = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.qr_code
# Create your models here.
