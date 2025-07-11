from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .models import Bus, Route, Schedule, Booking, UserProfile
from .forms import UserRegisterForm, UserLoginForm, BookingForm, UserProfileForm, SearchForm
from django.contrib import messages
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils import timezone

def home(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            origin = form.cleaned_data['origin']
            destination = form.cleaned_data['destination']
            date = form.cleaned_data['date']
            
            return redirect('bus_list', origin=origin, destination=destination, date=date.strftime('%Y-%m-%d'))
    else:
        form = SearchForm()
    
    popular_routes = Route.objects.all()[:6]
    
    # Calculate dates for today and tomorrow
    today = timezone.now().strftime('%Y-%m-%d')
    tomorrow = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    context = {
        'form': form,
        'popular_routes': popular_routes,
        'today': today,
        'tomorrow': tomorrow,
    }
    return render(request, 'tickets/home.html', context)

def bus_list(request, origin, destination, date):
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        messages.error(request, "Invalid date format")
        return redirect('home')
    
    schedules = Schedule.objects.filter(
        route__origin__icontains=origin,
        route__destination__icontains=destination,
        departure_time__date=date_obj
    ).select_related('bus', 'route', 'bus__company')
    
    # Calculate dates for navigation
    current_date = datetime.strptime(date, '%Y-%m-%d')
    previous_day = (current_date - timedelta(days=1)).strftime('%Y-%m-%d')
    next_day = (current_date + timedelta(days=1)).strftime('%Y-%m-%d')
    
    context = {
        'schedules': schedules,
        'origin': origin,
        'destination': destination,
        'date': date,
        'previous_day': previous_day,
        'next_day': next_day,
    }
    return render(request, 'tickets/bus_list.html', context)

@login_required
def booking(request, schedule_id):
    schedule = Schedule.objects.get(id=schedule_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            seat_numbers = form.cleaned_data['seat_numbers']
            num_seats = len(seat_numbers.split(','))
            
            if num_seats > schedule.available_seats:
                messages.error(request, "Not enough seats available")
                return redirect('bus_list', origin=schedule.route.origin, destination=schedule.route.destination, date=schedule.departure_time.strftime('%Y-%m-%d'))
            
            total_price = schedule.price * num_seats
            booking = Booking.objects.create(
                user=request.user,
                schedule=schedule,
                seat_numbers=seat_numbers,
                total_price=total_price
            )
            
            schedule.available_seats -= num_seats
            schedule.save()
            
            messages.success(request, "Booking successful!")
            return redirect('profile')
    else:
        form = BookingForm()
    
    context = {
        'schedule': schedule,
        'form': form,
        'available_seats': range(1, schedule.available_seats + 1)
    }
    return render(request, 'tickets/booking.html', context)

def user_register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create user profile
            UserProfile.objects.create(
                user=user,
                phone_number=form.cleaned_data['phone_number']
            )
            
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'tickets/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = UserLoginForm()
    return render(request, 'tickets/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def profile(request):
    bookings = Booking.objects.filter(user=request.user).select_related('schedule', 'schedule__bus', 'schedule__route')
    
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        profile_form = UserProfileForm(instance=request.user.userprofile)
    
    context = {
        'bookings': bookings,
        'profile_form': profile_form
    }
    return render(request, 'tickets/profile.html', context)

@login_required
def cancel_booking(request, booking_id):
    booking = Booking.objects.get(id=booking_id, user=request.user)
    
    if booking.status != 'Cancelled':
        booking.status = 'Cancelled'
        booking.save()
        
        # Return seats to availability
        num_seats = len(booking.seat_numbers.split(','))
        booking.schedule.available_seats += num_seats
        booking.schedule.save()
        
        messages.success(request, "Booking cancelled successfully")
    else:
        messages.warning(request, "Booking is already cancelled")
    
    return redirect('profile')