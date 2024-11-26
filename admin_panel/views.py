from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from gps.models import GpsPoint
from userwork.models import Shift
from trucks.models import Truck
from datetime import datetime

def user_stats_view(request):
    user_stats = {}
    shifts = Shift.objects.all()

    # Apply filters
    username_filter = request.GET.get('username', None)
    if username_filter:
        shifts = shifts.filter(username__icontains=username_filter)

    # Aggregate user stats
    for shift in shifts:
        username = shift.username
        if username not in user_stats:
            user_stats[username] = {
                'total_shifts': 0,
                'total_working_seconds': 0,
                'total_break_seconds': 0,
            }

        user_stats[username]['total_shifts'] += 1

        if shift.end_time and shift.start_time:
            working_time = (shift.end_time - shift.start_time).total_seconds()
            user_stats[username]['total_working_seconds'] += working_time

        for break_ in shift.breaks.all():
            if break_.end_time and break_.start_time:
                break_time = (break_.end_time - break_.start_time).total_seconds()
                user_stats[username]['total_break_seconds'] += break_time

    # Convert seconds to hours for display
    for username, stats in user_stats.items():
        stats['total_working_hours'] = stats['total_working_seconds'] / 3600
        stats['total_break_hours'] = stats['total_break_seconds'] / 3600

    # Sorting logic
    sort_key = request.GET.get('sort', 'username')  # Default sort by username
    sort_order = request.GET.get('order', 'asc')  # Default order is ascending

    if sort_key == 'username':
        sorted_stats = sorted(
            user_stats.items(),
            key=lambda x: x[0].lower(),  # Sort by username (case-insensitive)
            reverse=(sort_order == 'desc')
        )
    elif sort_key == 'shifts':
        sorted_stats = sorted(
            user_stats.items(),
            key=lambda x: x[1]['total_shifts'],
            reverse=(sort_order == 'desc')
        )
    elif sort_key == 'working_hours':
        sorted_stats = sorted(
            user_stats.items(),
            key=lambda x: x[1]['total_working_hours'],
            reverse=(sort_order == 'desc')
        )
    elif sort_key == 'break_hours':
        sorted_stats = sorted(
            user_stats.items(),
            key=lambda x: x[1]['total_break_hours'],
            reverse=(sort_order == 'desc')
        )
    else:
        sorted_stats = user_stats.items()  # Default to unsorted if invalid key

    # Prepare table data
    table_headers = [
        {'label': 'Username', 'sort_key': 'username'},
        {'label': 'Total Shifts', 'sort_key': 'shifts'},
        {'label': 'Total Working Hours', 'sort_key': 'working_hours'},
        {'label': 'Total Break Hours', 'sort_key': 'break_hours'},
    ]
    table_data = [
        [
            f'<a href="{reverse("user_shifts", args=[username])}" class="text-white">{username}</a>',
            stats['total_shifts'],
            f'{stats["total_working_hours"]:.2f}',
            f'{stats["total_break_hours"]:.2f}',
        ]
        for username, stats in sorted_stats
    ]

    return render(request, 'admin/user_stats.html', {
        'table_headers': table_headers,
        'table_data': table_data,
        'username_filter': username_filter,
        'sort_order': sort_order,
        'current_sort': sort_key,
    })


# Truck Statistics View
def truck_stats_view(request):
    truck_stats = {}
    trucks = Truck.objects.all()

    # Apply filtering
    truck_name_filter = request.GET.get('truck_name', None)
    if truck_name_filter:
        trucks = trucks.filter(name__icontains=truck_name_filter)

    # Collect truck stats
    for truck in trucks:
        truck_shifts = Shift.objects.filter(truck=truck)
        total_working_seconds = 0

        for shift in truck_shifts:
            if shift.end_time and shift.start_time:
                working_time = (shift.end_time - shift.start_time).total_seconds()
                total_working_seconds += working_time

        truck_stats[truck.name] = {
            'total_mileage': truck.milage,
            'total_shifts': truck_shifts.count(),
            'total_working_hours': total_working_seconds / 3600,
            'qr_code_path': f"/media/{truck.qr_code}.png",  # Path to QR code image
        }

    # Sorting logic
    sort_key = request.GET.get('sort', 'name')  # Default sort by truck name
    sort_order = request.GET.get('order', 'asc')  # Default order is ascending

    sorted_truck_stats = sorted(
        truck_stats.items(),
        key=lambda x: (
            x[0].lower() if sort_key == 'name' else
            x[1][sort_key]
        ),
        reverse=(sort_order == 'desc')
    )

    # Prepare table headers and data
    table_headers = [
        {'label': 'Truck Name', 'sort_key': 'name'},
        {'label': 'Total Mileage', 'sort_key': 'total_mileage'},
        {'label': 'Total Shifts', 'sort_key': 'total_shifts'},
        {'label': 'Total Working Hours', 'sort_key': 'total_working_hours'},
        {'label': 'QR Code', 'sort_key': ''},  # No sorting for QR code column
    ]
    table_data = [
        [
            truck_name,
            stats['total_mileage'],
            stats['total_shifts'],
            f'{stats["total_working_hours"]:.2f}',
            f'<a href="{stats["qr_code_path"]}" download="{truck_name}_QR.png" class="btn btn-sm btn-primary">Download QR Code</a>'
        ]
        for truck_name, stats in sorted_truck_stats
    ]

    return render(request, 'admin/truck_stats.html', {
        'table_headers': table_headers,
        'table_data': table_data,
        'truck_name_filter': truck_name_filter,
        'sort_order': sort_order,
        'current_sort': sort_key,
    })



def user_shifts_view(request, username):
    # Fetch all shifts for the user
    user_shifts = Shift.objects.filter(username=username)

    # Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            user_shifts = user_shifts.filter(start_time__date__gte=start_date)
        except ValueError:
            start_date = None

    if end_date:
        try:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            user_shifts = user_shifts.filter(start_time__date__lte=end_date)
        except ValueError:
            end_date = None

    # Calculate summary
    total_shifts = user_shifts.count()
    total_working_seconds = 0
    total_break_seconds = 0

    for shift in user_shifts:
        if shift.end_time and shift.start_time:
            working_time = (shift.end_time - shift.start_time).total_seconds()
            total_working_seconds += working_time

        for break_ in shift.breaks.all():
            if break_.end_time and break_.start_time:
                break_time = (break_.end_time - break_.start_time).total_seconds()
                total_break_seconds += break_time

    total_working_hours = total_working_seconds / 3600
    total_break_hours = total_break_seconds / 3600

    return render(request, 'admin/user_shifts.html', {
        'username': username,
        'user_shifts': user_shifts,
        'start_date': start_date,
        'end_date': end_date,
        'summary': {
            'total_shifts': total_shifts,
            'total_working_hours': total_working_hours,
            'total_break_hours': total_break_hours,
        }
    })

def create_gps_point_view(request):
    if request.method == 'POST':
        # Handle form submission
        name = request.POST.get('name')
        lat = request.POST.get('lat')
        lng = request.POST.get('lng')
        qr_code = request.POST.get('qr_code')

        # Save the new GPS point
        GpsPoint.objects.create(lat=lat, long=lng, name=name, qr_code=qr_code)
        return redirect('admin_stats')  # Redirect to the admin stats page or a success page

    return render(request, 'admin/create_gps_point.html')

def create_truck_view(request):
    return render(request, 'admin/create_truck.html')

def view_truck_qr_codes(request):
    # Fetch all trucks
    trucks = Truck.objects.all()

    # Prepare data for template
    trucks_data = []
    for truck in trucks:
        qr_code_path = f"/media/{truck.qr_code}.png"  # Build the path to the QR code image
        trucks_data.append({
            'name': truck.name,
            'mileage': truck.milage,
            'qr_code_path': qr_code_path
        })

    return render(request, 'admin/view_truck_qr_codes.html', {'trucks': trucks_data})

