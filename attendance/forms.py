import re
from django import forms
from .models import Event
from django.core.exceptions import ValidationError
import datetime

def is_valid_calendar_date(calendar_date):
    # calendar_dateを文字列に変換する
    calendar_date_str = calendar_date.strftime('%Y-%m-%d') if isinstance(calendar_date, datetime.date) else calendar_date
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    return re.match(pattern, calendar_date_str) is not None

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['full_name', 'gender', 'calendar_date', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'calendar_date': forms.DateInput(attrs={'type': 'date'}),
            'full_name': forms.TextInput(attrs={'placeholder': 'Full Name'}),
            'gender': forms.Select(choices=Event.GENDER_CHOICES),
        }

    
    def clean_calendar_date(self):
        calendar_date = self.cleaned_data.get('calendar_date')
        # ここで calendar_date の形式を検証し、問題があれば例外を発生させる
        if not is_valid_calendar_date(calendar_date):
            raise ValidationError('Invalid calendar date format')
        return calendar_date
