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
        
    def clean(self):
        cleaned_data = super().clean()
        calendar_date = cleaned_data.get('calendar_date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        # 日付と時間を組み合わせてdatetimeオブジェクトを作成
        if calendar_date and start_time:
            start_datetime = datetime.datetime.combine(calendar_date, start_time)
            cleaned_data['start_datetime'] = start_datetime
        if calendar_date and end_time:
            end_datetime = datetime.datetime.combine(calendar_date, end_time)
            cleaned_data['end_datetime'] = end_datetime

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        # start_datetimeとend_datetimeを使用してインスタンスを更新
        instance.start_time = self.cleaned_data.get('start_datetime', instance.start_time)
        instance.end_time = self.cleaned_data.get('end_datetime', instance.end_time)

        if commit:
            instance.save()
        return instance

    
    def clean_calendar_date(self):
        calendar_date = self.cleaned_data.get('calendar_date')
        # ここで calendar_date の形式を検証し、問題があれば例外を発生させる
        if not is_valid_calendar_date(calendar_date):
            raise ValidationError('Invalid calendar date format')
        return calendar_date
