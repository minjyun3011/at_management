from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['start_time', 'end_time', 'full_name', 'gender']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'full_name': forms.TextInput(attrs={'placeholder': 'Full Name'}),
            'gender': forms.Select(choices=Event.GENDER_CHOICES),
        }

