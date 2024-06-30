import re
from django import forms
from .models import User, ServiceTime
from django.core.exceptions import ValidationError
import datetime
from .models import Attendance_info


class UserForm(forms.ModelForm):
    service_type = forms.ChoiceField(
        choices=ServiceTime.SERVICE_TYPES,
        label='利用するサービス',
        required=True
    )

    class Meta:
        model = User
        fields = ['name', 'birthdate', 'gender', 'recipient_number', 'education_level', 'welfare_exemption', 'service_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'birthdate': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'recipient_number': forms.TextInput(attrs={'class': 'form-control'}),
            'education_level': forms.Select(attrs={'class': 'form-control'}),
            'welfare_exemption': forms.NumberInput(attrs={'class': 'form-control'}),
            'service_type': forms.Select(attrs={'class': 'form-control'})
        }


class AttendanceInfoForm(forms.ModelForm):
    class Meta:
        model = Attendance_info
        fields = ['calendar_date', 'start_time', 'end_time', 'status', 'transportation_to', 'transportation_from', 'absence_reason', 'updater', 'inputter']  # 新しいフィールドを追加
        widgets = {
            'calendar_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'transportation_to': forms.Select(attrs={'class': 'form-control'}),
            'transportation_from': forms.Select(attrs={'class': 'form-control'}),
            'absence_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'updater': forms.TextInput(attrs={'class': 'form-control'}),
            'inputter': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if status == Attendance_info.AttendanceStatus.PRESENT:
            if not start_time:
                self.add_error('start_time', '出席の場合、開始時間は必須です。')
            if not end_time:
                self.add_error('end_time', '出席の場合、終了時間は必須です。')
            if start_time and end_time and end_time <= start_time:
                self.add_error('end_time', '終了時間は開始時間より後である必要があります。')
        elif status == Attendance_info.AttendanceStatus.ABSENT:
            cleaned_data['start_time'] = None
            cleaned_data['end_time'] = None
            if not cleaned_data.get('absence_reason'):
                self.add_error('absence_reason', '欠席の場合、欠席理由は必須です。')

        return cleaned_data
    
    
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


# forms.py
from django import forms

class ServiceTimeForm(forms.Form):
    WEEKDAYS = [
        ('mon', '月曜日'),
        ('tue', '火曜日'),
        ('wed', '水曜日'),
        ('thu', '木曜日'),
        ('fri', '金曜日'),
        ('sat', '土曜日'),
        ('sun', '日曜日'),
    ]

    SERVICE_TYPES = [
        ('group_morning', '集団 (午前)'),
        ('group_afternoon', '集団 (午後)'),
        ('individual_morning', '個別（午前）'),
        ('individual_afternoon', '個別 (午後)'),
        ('after_school', '放課後デイサービス (個別午後)'),
    ]

    def __init__(self, *args, **kwargs):
        super(ServiceTimeForm, self).__init__(*args, **kwargs)
        for day in self.WEEKDAYS:
            self.fields[f"{day[0]}_select"] = forms.BooleanField(label=f"{day[1]} 選択", required=False)
            for service in self.SERVICE_TYPES:
                self.fields[f"{day[0]}_{service[0]}_start"] = forms.TimeField(
                    label=f"{day[1]} {service[1]} 開始時間",
                    required=False,
                    initial='09:00',
                    widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time'})
                )
                self.fields[f"{day[0]}_{service[0]}_end"] = forms.TimeField(
                    label=f"{day[1]} {service[1]} 終了時間",
                    required=False,
                    initial='17:00',
                    widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time'})
                )

    def clean(self):
        cleaned_data = super().clean()
        for day in self.WEEKDAYS:
            for service in self.SERVICE_TYPES:
                start_time = cleaned_data.get(f"{day[0]}_{service[0]}_start")
                end_time = cleaned_data.get(f"{day[0]}_{service[0]}_end")
                if start_time and end_time:
                    if start_time >= end_time:
                        self.add_error(f"{day[0]}_{service[0]}_end", "終了時間は開始時間より後でなければなりません。")
        return cleaned_data
