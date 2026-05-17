from django import forms
from .models import Facility

class FacilityForm(forms.ModelForm):

    class Meta:
        model = Facility
        fields = ['facility_name', 'location', 'capacity']

        widgets = {
            'facility_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'location': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'capacity': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
        }