# tickets/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .models import Bus, Booking
from .forms import RegisterForm, BookingForm
from django.contrib.auth.models import User

def home(request):
    return render(request, 'tickets/home.html')

def bus_list(request):
    buses = Bus.objects.all().order_by('departure_time')
    return render(request, 'tickets/bus_list.html', {'buses': buses})

@login_required
def booking(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id)
    booked_seats = Booking.objects.filter(bus=bus).values_list('seat_number', flat=True)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            seat_number = form.cleaned_data['seat_number']
            if seat_number in booked_seats or seat_number > bus.total_seats:
                form.add_error('seat_number', 'Seat already booked or invalid seat number.')
            else:
                Booking.objects.create(user=request.user, bus=bus, seat_number=seat_number)
                return redirect('profile')
    else:
        form = BookingForm()
    return render(request, 'tickets/booking.html', {'bus': bus, 'form': form, 'booked_seats': booked_seats})

@login_required
def profile(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_time')
    return render(request, 'tickets/profile.html', {'bookings': bookings})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Optionally save phone number in UserProfile
            user.refresh_from_db()
            user.userprofile.phone = form.cleaned_data.get('phone')
            user.userprofile.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'tickets/register.html', {'form': form})

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('home')
    buses = Bus.objects.all()
    bookings = Booking.objects.all()
    return render(request, 'tickets/admin_dashboard.html', {'buses': buses, 'bookings': bookings})
