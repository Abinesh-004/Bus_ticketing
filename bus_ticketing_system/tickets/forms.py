from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Booking, UserProfile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=15)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password1', 'password2']

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['seat_numbers']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address', 'id_proof']

class SearchForm(forms.Form):
    origin = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'From'}))
    destination = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'To'}))
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))