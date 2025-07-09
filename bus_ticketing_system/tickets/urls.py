# tickets/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('buses/', views.bus_list, name='bus_list'),
    path('booking/<int:bus_id>/', views.booking, name='booking'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register, name='register'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
