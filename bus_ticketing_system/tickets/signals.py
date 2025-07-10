from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Booking, Bus, Seat

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when User is created"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved"""
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()

@receiver(post_save, sender=Bus)
def create_bus_seats(sender, instance, created, **kwargs):
    """Create seats when a bus is created"""
    if created:
        for i in range(1, instance.total_seats + 1):
            seat_type = 'window' if i % 4 in [1, 0] else 'aisle'
            Seat.objects.create(
                bus=instance,
                seat_number=str(i),
                seat_type=seat_type
            )

@receiver(post_delete, sender=Booking)
def restore_seats_on_booking_delete(sender, instance, **kwargs):
    """Restore available seats when booking is deleted"""
    if instance.booking_status in ['confirmed', 'pending']:
        seat_count = len(instance.seat_numbers.split(','))
        instance.trip.available_seats += seat_count
        instance.trip.save()