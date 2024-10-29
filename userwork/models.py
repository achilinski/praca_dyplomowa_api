from django.db import models

# Create your models here.

class Shift(models.Model):
    username = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    truck = models.ForeignKey('trucks.Truck', on_delete=models.CASCADE)

    def __str__(self):
        return self.username


