# myapp/forms.py
from django import forms
from .models import Rental, UserProfile, Donation, USER_TYPE_CHOICES

class RentalForm(forms.ModelForm):
    class Meta:
        model = Rental
        fields = ['start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['name', 'last_name', 'address', 'user_type']
        widgets = {
            'user_type': forms.Select(choices=USER_TYPE_CHOICES),
            'address': forms.Textarea(attrs={'rows': 4}),
        }

class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['product_name', 'description', 'image']  # Add image field
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'image': forms.ClearableFileInput(attrs={'accept': 'image/*'}),  # Restrict to image files
        }