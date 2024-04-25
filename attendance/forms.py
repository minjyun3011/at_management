import re
from django import forms
from .models import Event, User
from django.core.exceptions import ValidationError
import datetime
from .models import Attendance_info

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'birthdate', 'gender', 'recipient_number', 'education_level', 'welfare_exemption']
        widgets = {
            'birthdate': forms.DateInput(attrs={'type': 'date'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'recipient_number': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'education_level': forms.Select(attrs={'class': 'form-control'}),
            'welfare_exemption': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class AttendanceInfoForm(forms.ModelForm):
    class Meta:
        model = Attendance_info
        fields = ['calendar_date', 'start_time', 'end_time', 'status', 'transportation_to', 'transportation_from', 'absence_reason']
        widgets = {
            'calendar_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'transportation_to': forms.Select(attrs={'class': 'form-control'}),
            'transportation_from': forms.Select(attrs={'class': 'form-control'}),
            'absence_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_calendar_date(self):
        date = self.cleaned_data.get('calendar_date')
        # ここで日付の形式や論理を検証する
        if not date:  # 日付が正しくない場合
            raise ValidationError('Invalid date format')
        return date

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        if start_time and end_time and end_time <= start_time:
            raise ValidationError('End time must be after start time.')
        return cleaned_data
    
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

class CheckUserForm(forms.Form):
    recipient_number = forms.CharField(
        label="受給者番号",
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '受給者番号を入力'})
    )

    def clean_recipient_number(self):
        recipient_number = self.cleaned_data.get('recipient_number')
        if not User.objects.filter(recipient_number=recipient_number).exists():
            raise forms.ValidationError("この受給者番号は登録されていません。")
        return recipient_number

