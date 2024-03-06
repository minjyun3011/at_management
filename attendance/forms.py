import re
from django import forms
from .models import Event
from django.core.exceptions import ValidationError

def is_valid_calendar_date(calendar_date):
    # カレンダー日付形式の正規表現パターン
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    # 正規表現パターンにマッチするかどうかをチェック
    if re.match(pattern, calendar_date):
        return True
    else:
        return False

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['start_time', 'end_time', 'full_name', 'gender', 'calendar_date']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'full_name': forms.TextInput(attrs={'placeholder': 'Full Name'}),
            'gender': forms.Select(choices=Event.GENDER_CHOICES),
            'calendar_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean_calendar_date(self):
        calendar_date = self.cleaned_data.get('calendar_date')
        # ここで calendar_date の形式を検証し、問題があれば例外を発生させる
        if not self.is_valid_calendar_date(calendar_date):
            raise ValidationError('Invalid calendar date format')
        return calendar_date
