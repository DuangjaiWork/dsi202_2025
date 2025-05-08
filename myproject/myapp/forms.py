# myapp/forms.py
from django import forms
from .models import Rental, UserProfile, Donation, USER_TYPE_CHOICES

class RentalForm(forms.ModelForm):
    rental_months = forms.ChoiceField(
        choices=[(i, f"{i} Month{'s' if i > 1 else ''}") for i in range(1, 13)],
        widget=forms.Select(attrs={'class': 'w-full p-3 border border-[#009aa6] rounded-lg'}),
    )

    class Meta:
        model = Rental
        fields = ['start_date', 'rental_months']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
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
        fields = ['product_name', 'description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'image': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }