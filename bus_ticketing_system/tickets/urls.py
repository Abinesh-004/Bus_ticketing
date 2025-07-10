from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('buses/<str:origin>/<str:destination>/<str:date>/<int:passengers>/', 
         views.bus_list, name='bus_list'),
    path('booking/<int:trip_id>/', views.booking_view, name='booking'),
    path('payment/<uuid:booking_id>/', views.payment_view, name='payment'),
    path('booking-detail/<uuid:booking_id>/', views.booking_detail, name='booking_detail'),
    path('cancel-booking/<uuid:booking_id>/', views.cancel_booking, name='cancel_booking'),
    
    # User authentication
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='tickets/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('buses/', views.bus_list, name='bus_list'),  # New pattern without args
    
    # Password reset
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='tickets/password_reset.html'),
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='tickets/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='tickets/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='tickets/password_reset_complete.html'),
         name='password_reset_complete'),
    
    # API endpoints
    path('api/seat-status/<int:trip_id>/', views.get_seat_status, name='seat_status_api'),
    path('api/search-cities/', views.search_cities, name='search_cities_api'),
    
    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]