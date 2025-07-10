from django.contrib import admin
from .models import *

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone_number')
    list_filter = ('created_at',)

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'origin', 'destination', 'distance', 'is_active')
    list_filter = ('is_active', 'origin', 'destination')
    search_fields = ('name', 'origin', 'destination')

@admin.register(BusOperator)
class BusOperatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'license_number', 'contact_person', 'phone', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'license_number', 'contact_person')

@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ('number', 'operator', 'type', 'total_seats', 'is_active')
    list_filter = ('type', 'is_active', 'operator')
    search_fields = ('number', 'operator__name')

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('bus', 'route', 'departure_time', 'arrival_time', 'base_fare', 'is_active')
    list_filter = ('is_active', 'bus__type', 'effective_from')
    search_fields = ('bus__number', 'route__name')

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('schedule', 'trip_date', 'status', 'available_seats')
    list_filter = ('status', 'trip_date', 'schedule__bus__type')
    search_fields = ('schedule__bus__number', 'schedule__route__name')
    date_hierarchy = 'trip_date'

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('bus', 'seat_number', 'seat_type', 'is_available')
    list_filter = ('seat_type', 'is_available', 'bus__type')
    search_fields = ('bus__number', 'seat_number')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'user', 'passenger_name', 'trip', 'total_seats', 'total_amount', 'booking_status', 'payment_status')
    list_filter = ('booking_status', 'payment_status', 'booking_date')
    search_fields = ('booking_id', 'user__username', 'passenger_name', 'passenger_phone')
    date_hierarchy = 'booking_date'
    readonly_fields = ('booking_id', 'booking_date')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'amount', 'payment_method', 'payment_status', 'payment_date')
    list_filter = ('payment_method', 'payment_status', 'payment_date')
    search_fields = ('booking__booking_id', 'transaction_id', 'reference_number')
    date_hierarchy = 'payment_date'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'booking', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'booking__booking_id')
    date_hierarchy = 'created_at'