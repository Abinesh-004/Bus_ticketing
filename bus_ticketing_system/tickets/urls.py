from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/<str:origin>/<str:destination>/<str:date>/', views.bus_list, name='bus_list'),
    path('booking/<int:schedule_id>/', views.booking, name='booking'),
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
]