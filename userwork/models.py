from django.db import models


# Create your models here.

class Shift(models.Model):
    username = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    truck = models.ForeignKey('trucks.Truck', on_delete=models.CASCADE)

    def __str__(self):
        return self.username
    
    def total_break_time(self):
        breaks = self.break_set.all()
        total_seconds = sum((br.end_time - br.start_time).total_seconds() for br in breaks)
        return total_seconds
    
class Break(models.Model):
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='breaks')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)

    def __str__(self):
        return f"Break for {self.shift.username} from {self.start_time} to {self.end_time or 'ongoing'}"
    
class PlannedShift(models.Model):
    username = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    truck = models.ForeignKey('trucks.Truck', on_delete=models.CASCADE)
    points = models.ManyToManyField('gps.GpsPoint', through='PlannedShiftPoint')
    was_active = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    def ordered_gps_points(self):
        return self.points.all().order_by('plannedshiftpoint__order')
    
class PlannedShiftPoint(models.Model):
    planned_shift = models.ForeignKey('PlannedShift', on_delete=models.CASCADE)
    gps_point = models.ForeignKey('gps.GpsPoint', on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']  # Ensures that points are ordered by the 'order' field

    def __str__(self):
        return f"{self.planned_shift} - {self.gps_point} (Order: {self.order})"


