from django.contrib import admin
from django.db.models import Sum, Count
from userwork.models import Shift
from trucks.models import Truck
from django.db.models.functions import Coalesce
from django.db.models import F, ExpressionWrapper, DurationField


class UserStatsAdmin(admin.ModelAdmin):
    change_list_template = 'admin/user_stats.html'

    def changelist_view(self, request, extra_context=None):
        # Annotate each shift with its duration
        shifts = Shift.objects.annotate(
            shift_duration=ExpressionWrapper(
                Coalesce(F('end_time'), F('start_time')) - F('start_time'),
                output_field=DurationField()
            )
        )

        # Calculate statistics in Python
        stats = {}
        for shift in shifts:
            username = shift.username
            if username not in stats:
                stats[username] = {
                    'total_shifts': 0,
                    'total_working_seconds': 0,
                    'total_break_seconds': 0,
                }
            stats[username]['total_shifts'] += 1
            stats[username]['total_working_seconds'] += shift.shift_duration.total_seconds()
            stats[username]['total_break_seconds'] += sum(
                (break_.end_time - break_.start_time).total_seconds()
                for break_ in shift.breaks.all() if break_.end_time
            )

        # Format statistics for the template
        extra_context = {'stats': stats}
        return super().changelist_view(request, extra_context=extra_context)

class TruckAdmin(admin.ModelAdmin):
    list_display = ('name', 'milage', 'get_total_shifts', 'get_total_work_hours')

    def get_total_shifts(self, obj):
        return obj.shift_set.count()
    get_total_shifts.short_description = 'Total Shifts'

    def get_total_work_hours(self, obj):
        shifts = obj.shift_set.aggregate(
            total_hours=Sum('end_time') - Sum('start_time')
        )
        return shifts['total_hours']
    get_total_work_hours.short_description = 'Total Work Hours'

admin.site.register(Shift, UserStatsAdmin)
admin.site.register(Truck, TruckAdmin)
