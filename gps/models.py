from django.db import models



class GpsPoint(models.Model):
    lat = models.DecimalField(max_digits=8, decimal_places=6, default=None)
    long = models.DecimalField(max_digits=8, decimal_places=6, default=None)
    qr_code = models.CharField(max_length=255, unique=True, default=None)
    name = models.CharField(max_length=255, unique=False, null=True, default=None)

    def __str__(self) -> str:
        #eturn [self.lat, self.long]
        return f"{self.lat}, {self.long}"
    

class GpsPointList(models.Model):
    username = models.CharField(max_length=100, default=None)
    point_set = models.ManyToManyField(GpsPoint)

