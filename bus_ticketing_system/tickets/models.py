# tickets/models.py

from django.db import models
from django.contrib.auth.models import User

class Route(models.Model):
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    duration = models.DurationField()

    def __str__(self):
        return f"{self.origin} to {self.destination}"

class Bus(models.Model):
    bus_number = models.CharField(max_length=20, unique=True)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    total_seats = models.PositiveIntegerField(default=40)
    departure_time = models.DateTimeField()

    def __str__(self):
        return f"{self.bus_number} on {self.route}"

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    seat_number = models.PositiveIntegerField()
    booking_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('bus', 'seat_number')

    def __str__(self):
        return f"{self.user.username} booked seat {self.seat_number} on {self.bus}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} Profile"

