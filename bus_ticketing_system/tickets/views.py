from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import *
from .forms import *
import json

def home(request):
    """Home page with bus search functionality"""
    form = BusSearchForm()
    popular_routes = Route.objects.filter(is_active=True)[:6]
    
    if request.method == 'POST':
        form = BusSearchForm(request.POST)
        if form.is_valid():
            origin = form.cleaned_data['origin']
            destination = form.cleaned_data['destination']
            travel_date = form.cleaned_data['travel_date']
            passengers = form.cleaned_data['passengers']
            
            return redirect('bus_list', 
                          origin=origin, 
                          destination=destination,
                          date=travel_date.strftime('%Y-%m-%d'),
                          passengers=passengers)
    
    context = {
        'form': form,
        'popular_routes': popular_routes,
    }
    return render(request, 'tickets/home.html', context)

def bus_list(request, origin, destination, date, passengers):
    """Display available buses for the search criteria"""
    try:
        travel_date = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        messages.error(request, "Invalid date format")
        return redirect('home')
    
    # Find routes matching the origin and destination
    routes = Route.objects.filter(
        Q(origin__icontains=origin) & Q(destination__icontains=destination),
        is_active=True
    )
    
    available_trips = []
    for route in routes:
        # Get schedules for this route
        schedules = Schedule.objects.filter(
            route=route,
            is_active=True,
            effective_from__lte=travel_date
        ).filter(
            Q(effective_to__isnull=True) | Q(effective_to__gte=travel_date)
        )
        
        for schedule in schedules:
            # Get or create trip for this date
            trip, created = Trip.objects.get_or_create(
                schedule=schedule,
                trip_date=travel_date,
                defaults={'available_seats': schedule.bus.total_seats}
            )
            
            if trip.available_seats >= int(passengers) and trip.status == 'scheduled':
                available_trips.append({
                    'trip': trip,
                    'schedule': schedule,
                    'route': route,
                    'bus': schedule.bus,
                    'operator': schedule.bus.operator,
                })
    
    context = {
        'trips': available_trips,
        'origin': origin,
        'destination': destination,
        'travel_date': travel_date,
        'passengers': passengers,
        'search_performed': True,
    }
    return render(request, 'tickets/bus_list.html', context)

@login_required
def booking_view(request, trip_id):
    """Booking page with seat selection"""
    trip = get_object_or_404(Trip, id=trip_id)
    passengers = request.GET.get('passengers', 1)
    
    # Get existing bookings for this trip to show occupied seats
    existing_bookings = Booking.objects.filter(
        trip=trip,
        booking_status__in=['confirmed', 'pending']
    )
    
    occupied_seats = []
    for booking in existing_bookings:
        occupied_seats.extend(booking.seat_numbers.split(','))
    
    # Generate seat layout
    total_seats = trip.schedule.bus.total_seats
    seats_per_row = 4  # Common bus layout
    seat_layout = []
    
    for i in range(1, total_seats + 1):
        seat_number = str(i)
        seat_layout.append({
            'number': seat_number,
            'is_occupied': seat_number in occupied_seats,
            'type': 'window' if i % seats_per_row in [1, 0] else 'aisle'
        })
    
    if request.method == 'POST':
        form = BookingForm(request.POST, user=request.user)
        selected_seats = request.POST.get('selected_seats', '').split(',')
        selected_seats = [seat.strip() for seat in selected_seats if seat.strip()]
        
        if form.is_valid() and selected_seats:
            if len(selected_seats) == int(passengers):
                # Check if seats are still available
                current_bookings = Booking.objects.filter(
                    trip=trip,
                    booking_status__in=['confirmed', 'pending']
                )
                current_occupied = []
                for booking in current_bookings:
                    current_occupied.extend(booking.seat_numbers.split(','))
                
                if any(seat in current_occupied for seat in selected_seats):
                    messages.error(request, "Some selected seats are no longer available")
                    return redirect('booking', trip_id=trip_id)
                
                # Create booking
                booking = form.save(commit=False)
                booking.user = request.user
                booking.trip = trip
                booking.seat_numbers = ','.join(selected_seats)
                booking.total_seats = len(selected_seats)
                booking.total_amount = trip.schedule.base_fare * len(selected_seats)
                booking.save()
                
                # Update available seats
                trip.available_seats -= len(selected_seats)
                trip.save()
                
                messages.success(request, f"Booking created successfully! Booking ID: {booking.booking_id}")
                return redirect('payment', booking_id=booking.booking_id)
            else:
                messages.error(request, f"Please select exactly {passengers} seat(s)")
        else:
            messages.error(request, "Please fill all required fields and select seats")
    else:
        form = BookingForm(user=request.user)
    
    context = {
        'trip': trip,
        'form': form,
        'passengers': passengers,
        'seat_layout': seat_layout,
        'total_seats': total_seats,
        'seats_per_row': seats_per_row,
        'occupied_seats': occupied_seats,
    }
    return render(request, 'tickets/booking.html', context)

@login_required
def payment_view(request, booking_id):
    """Payment processing page"""
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    
    if booking.payment_status == 'paid':
        messages.info(request, "This booking has already been paid")
        return redirect('booking_detail', booking_id=booking_id)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']
            
            # Create payment record
            payment = Payment.objects.create(
                booking=booking,
                amount=booking.total_amount,
                payment_method=payment_method,
                payment_status='processing'
            )
            
            # Simulate payment processing
            if payment_method == 'cash':
                payment.payment_status = 'pending'
                booking.booking_status = 'confirmed'
                booking.payment_status = 'pending'
                messages.success(request, "Booking confirmed! Please pay cash during boarding.")
            else:
                # For demo purposes, mark as completed
                payment.payment_status = 'completed'
                payment.transaction_id = f"TXN{payment.id}{timezone.now().strftime('%Y%m%d%H%M%S')}"
                booking.booking_status = 'confirmed'
                booking.payment_status = 'paid'
                messages.success(request, "Payment successful! Your booking is confirmed.")
            
            payment.save()
            booking.save()
            
            return redirect('booking_detail', booking_id=booking_id)
    else:
        form = PaymentForm()
    
    context = {
        'booking': booking,
        'form': form,
    }
    return render(request, 'tickets/payment.html', context)

@login_required
def booking_detail(request, booking_id):
    """Display booking details"""
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    payments = Payment.objects.filter(booking=booking)
    
    context = {
        'booking': booking,
        'payments': payments,
    }
    return render(request, 'tickets/booking_detail.html', context)

@login_required
def profile_view(request):
    """User profile page with booking history"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    # Get user bookings
    bookings = Booking.objects.filter(user=request.user).select_related('trip__schedule__bus', 'trip__schedule__route')
    
    context = {
        'form': form,
        'profile': profile,
        'bookings': bookings,
    }
    return render(request, 'tickets/profile.html', context)

def register_view(request):
    """User registration"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Account created for {username}! You can now login.")
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'tickets/register.html', {'form': form})

@login_required
def cancel_booking(request, booking_id):
    """Cancel a booking"""
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    
    if booking.booking_status == 'cancelled':
        messages.info(request, "This booking is already cancelled")
        return redirect('profile')
    
    if request.method == 'POST':
        cancellation_reason = request.POST.get('cancellation_reason', '')
        
        # Update booking status
        booking.booking_status = 'cancelled'
        booking.cancellation_reason = cancellation_reason
        booking.save()
        
        # Update trip available seats
        seat_count = len(booking.seat_numbers.split(','))
        booking.trip.available_seats += seat_count
        booking.trip.save()
        
        messages.success(request, "Booking cancelled successfully")
        return redirect('profile')
    
    return render(request, 'tickets/cancel_booking.html', {'booking': booking})

# API Views for AJAX requests
@login_required
def get_seat_status(request, trip_id):
    """API endpoint to get current seat status"""
    trip = get_object_or_404(Trip, id=trip_id)
    
    # Get occupied seats
    bookings = Booking.objects.filter(
        trip=trip,
        booking_status__in=['confirmed', 'pending']
    )
    
    occupied_seats = []
    for booking in bookings:
        occupied_seats.extend(booking.seat_numbers.split(','))
    
    return JsonResponse({
        'occupied_seats': occupied_seats,
        'available_seats': trip.available_seats
    })

def search_cities(request):
    """API endpoint for city search autocomplete"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'cities': []})
    
    # Get unique cities from routes
    origins = Route.objects.filter(origin__icontains=query, is_active=True).values_list('origin', flat=True).distinct()
    destinations = Route.objects.filter(destination__icontains=query, is_active=True).values_list('destination', flat=True).distinct()
    
    cities = list(set(list(origins) + list(destinations)))
    cities.sort()
    
    return JsonResponse({'cities': cities[:10]})

# Admin views (basic)
@login_required
def admin_dashboard(request):
    """Basic admin dashboard"""
    if not request.user.is_staff:
        messages.error(request, "Access denied")
        return redirect('home')
    
    # Get basic statistics
    total_bookings = Booking.objects.count()
    total_users = User.objects.count()
    total_buses = Bus.objects.count()
    today_bookings = Booking.objects.filter(booking_date__date=timezone.now().date()).count()
    
    recent_bookings = Booking.objects.select_related('user', 'trip__schedule__bus').order_by('-booking_date')[:10]
    
    context = {
        'total_bookings': total_bookings,
        'total_users': total_users,
        'total_buses': total_buses,
        'today_bookings': today_bookings,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'tickets/admin_dashboard.html', context)