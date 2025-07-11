from django.contrib import admin
from .models import BusCompany, Route, Bus, Schedule, Booking, UserProfile

class BusCompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_number', 'email')
    search_fields = ('name', 'contact_number')

class RouteAdmin(admin.ModelAdmin):
    list_display = ('origin', 'destination', 'distance', 'estimated_time')
    search_fields = ('origin', 'destination')

class BusAdmin(admin.ModelAdmin):
    list_display = ('company', 'bus_number', 'bus_type', 'total_seats')
    list_filter = ('company', 'bus_type')
    search_fields = ('bus_number',)

class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('bus', 'route', 'departure_time', 'arrival_time', 'price', 'available_seats')
    list_filter = ('bus__company', 'route')
    search_fields = ('bus__bus_number', 'route__origin', 'route__destination')

class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'schedule', 'seat_numbers', 'booking_date', 'total_price', 'status')
    list_filter = ('status', 'schedule__bus__company')
    search_fields = ('user__username', 'payment_reference')

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')
    search_fields = ('user__username', 'phone_number')

admin.site.register(BusCompany, BusCompanyAdmin)
admin.site.register(Route, RouteAdmin)
admin.site.register(Bus, BusAdmin)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(UserProfile, UserProfileAdmin)