from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class BusCompany(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='company_logos/', null=True, blank=True)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()

    def __str__(self):
        return self.name

class Route(models.Model):
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    distance = models.FloatField(help_text="Distance in kilometers")
    estimated_time = models.DurationField(help_text="Estimated travel time")

    class Meta:
        unique_together = ('origin', 'destination')

    def __str__(self):
        return f"{self.origin} to {self.destination}"

class Bus(models.Model):
    BUS_TYPES = (
        ('AC', 'Air Conditioned'),
        ('Non-AC', 'Non Air Conditioned'),
        ('Deluxe', 'Deluxe'),
        ('Sleeper', 'Sleeper'),
    )

    company = models.ForeignKey(BusCompany, on_delete=models.CASCADE)
    bus_number = models.CharField(max_length=20)
    bus_type = models.CharField(max_length=20, choices=BUS_TYPES)
    total_seats = models.PositiveIntegerField()
    amenities = models.TextField(blank=True)
    image = models.ImageField(upload_to='bus_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.company.name} - {self.bus_number}"

class Schedule(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    available_seats = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.bus} on {self.departure_time}"

class Booking(models.Model):
    STATUS_CHOICES = (
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Pending', 'Pending'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    seat_numbers = models.CharField(max_length=100)
    booking_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Confirmed')
    payment_reference = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Booking #{self.id} by {self.user.username}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    address = models.TextField(blank=True)
    id_proof = models.ImageField(upload_to='id_proofs/', null=True, blank=True)

    def __str__(self):
        return self.user.username