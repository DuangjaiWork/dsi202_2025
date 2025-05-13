# myapp/forms.py
from django import forms
from .models import Rental, UserProfile, Donation, Review, USER_TYPE_CHOICES, Report
import re

class RentalForm(forms.ModelForm):
    rental_months = forms.ChoiceField(
        choices=[(i, f"{i}") for i in range(1, 13)],
        widget=forms.Select(attrs={'class': 'w-full p-3 border border-[#009aa6] rounded-lg'}),
    )

    class Meta:
        model = Rental
        fields = ['start_date', 'rental_months']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full p-3 border border-[#009aa6] rounded-lg'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['name', 'last_name', 'address', 'phone_number', 'user_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full p-3 border border-[#009aa6] rounded-lg'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full p-3 border border-[#009aa6] rounded-lg'}),
            'address': forms.Textarea(attrs={'rows': 4, 'class': 'w-full p-3 border border-[#009aa6] rounded-lg'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full p-3 border border-[#009aa6] rounded-lg', 'type': 'tel', 'placeholder': '+6634567890'}),
            'user_type': forms.Select(choices=USER_TYPE_CHOICES, attrs={'class': 'w-full p-3 border border-[#009aa6] rounded-lg'}),
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Example: Must start with "+" and have 10-15 digits
            if not re.match(r'^\+\d{10,15}$', phone_number):
                raise forms.ValidationError("Phone number must start with '+' and contain 10-15 digits.")
        return phone_number

class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['product_name', 'description', 'image']
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'w-full p-3 border border-[#009aa6] rounded-lg'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'w-full p-3 border border-[#009aa6] rounded-lg'}),
            'image': forms.ClearableFileInput(attrs={'accept': 'image/*', 'class': 'w-full p-3 border border-[#009aa6] rounded-lg'}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['content', 'rating']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'class': 'w-full p-3 border border-[#009aa6] rounded-lg'}),
            'rating': forms.Select(choices=[(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(1, 6)], attrs={'class': 'w-full p-3 border border-[#009aa6] rounded-lg'}),
        }

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['subject', 'description', 'image']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'w-full p-3 border border-[#009aa6] rounded-lg'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'w-full p-3 border border-[#009aa6] rounded-lg'}),
            'image': forms.ClearableFileInput(attrs={'accept': 'image/*', 'class': 'w-full p-3 border border-[#009aa6] rounded-lg'}),
        }
