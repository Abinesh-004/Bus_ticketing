from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

class Route(models.Model):
    name = models.CharField(max_length=100, unique=True)
    origin = models.CharField(max_length=50)
    destination = models.CharField(max_length=50)
    distance = models.FloatField(help_text="Distance in kilometers")
    duration = models.DurationField(help_text="Estimated travel time")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['origin', 'destination']
    
    def __str__(self):
        return f"{self.origin} to {self.destination}"

class BusOperator(models.Model):
    name = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True)
    contact_person = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Bus(models.Model):
    BUS_TYPES = [
        ('regular', 'Regular'),
        ('deluxe', 'Deluxe'),
        ('ac', 'AC'),
        ('sleeper', 'Sleeper'),
        ('tourist', 'Tourist'),
    ]
    
    operator = models.ForeignKey(BusOperator, on_delete=models.CASCADE)
    number = models.CharField(max_length=20, unique=True)
    type = models.CharField(max_length=20, choices=BUS_TYPES, default='regular')
    total_seats = models.IntegerField(validators=[MinValueValidator(10), MaxValueValidator(60)])
    amenities = models.TextField(blank=True, help_text="Comma-separated amenities")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['number']
    
    def __str__(self):
        return f"{self.number} ({self.operator.name})"

class Schedule(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    base_fare = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['departure_time']
        unique_together = ['bus', 'route', 'departure_time']
    
    def __str__(self):
        return f"{self.bus.number} - {self.route.name} ({self.departure_time})"

class Trip(models.Model):
    TRIP_STATUS = [
        ('scheduled', 'Scheduled'),
        ('boarding', 'Boarding'),
        ('departed', 'Departed'),
        ('arrived', 'Arrived'),
        ('cancelled', 'Cancelled'),
    ]
    
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    trip_date = models.DateField()
    status = models.CharField(max_length=20, choices=TRIP_STATUS, default='scheduled')
    available_seats = models.IntegerField()
    actual_departure = models.DateTimeField(null=True, blank=True)
    actual_arrival = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['trip_date', 'schedule__departure_time']
        unique_together = ['schedule', 'trip_date']
    
    def __str__(self):
        return f"{self.schedule.bus.number} - {self.trip_date} ({self.status})"
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.available_seats = self.schedule.bus.total_seats
        super().save(*args, **kwargs)

class Seat(models.Model):
    SEAT_TYPES = [
        ('window', 'Window'),
        ('aisle', 'Aisle'),
        ('middle', 'Middle'),
    ]
    
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=10)
    seat_type = models.CharField(max_length=20, choices=SEAT_TYPES)
    is_available = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['bus', 'seat_number']
        ordering = ['seat_number']
    
    def __str__(self):
        return f"{self.bus.number} - Seat {self.seat_number}"

class Booking(models.Model):
    BOOKING_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]
    
    booking_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, null=True, blank=True)  # temporarily nullable for migration
    passenger_name = models.CharField(max_length=100, default='Unknown Passenger')
    passenger_phone = models.CharField(max_length=15, default='0000000000')
    passenger_email = models.EmailField(default='unknown@example.com')
    seat_numbers = models.CharField(max_length=100, help_text="Comma-separated seat numbers", default='N/A')
    total_seats = models.IntegerField(validators=[MinValueValidator(1)], default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    booking_status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    booking_date = models.DateTimeField(auto_now_add=True)
    cancellation_reason = models.TextField(blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-booking_date']
    
    def __str__(self):
        return f"Booking {self.booking_id} - {self.passenger_name}"
    
    def save(self, *args, **kwargs):
        if self.booking_status == 'cancelled' and not self.cancelled_at:
            self.cancelled_at = timezone.now()
        super().save(*args, **kwargs)

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('esewa', 'eSewa'),
        ('khalti', 'Khalti'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    reference_number = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Payment {self.id} - {self.booking.booking_id}"

class Review(models.Model):
    RATINGS = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATINGS)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review by {self.user.username} - {self.rating} stars"
