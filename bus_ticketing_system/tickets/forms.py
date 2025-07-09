# tickets/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Booking

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2']

class BookingForm(forms.ModelForm):
    seat_number = forms.IntegerField(min_value=1)

    class Meta:
        model = Booking
        fields = ['seat_number']
