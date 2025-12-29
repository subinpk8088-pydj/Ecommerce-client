# forms.py
from django import forms
from .models import UserAddress

class UserAddressForm(forms.ModelForm):
    class Meta:
        model = UserAddress
        fields = ['full_name', 'phone', 'email', 'address', 'city', 'state', 'pincode']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
        }