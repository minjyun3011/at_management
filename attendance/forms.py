from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['start_time', 'end_time', 'full_name', 'gender']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'gender': forms.Select(choices=Event.GENDER_CHOICES),
        }

class CalendarForm(forms.ModelForm):
    class Meta:
        model = Event
        # イベントモデルの適用するフィールドを指定
        fields = ['start_time', 'end_time', 'full_name', 'gender']
        # 特定のフィールドにカスタムウィジェットを適用
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'full_name': forms.TextInput(attrs={'placeholder': 'Full Name'}),
            'gender': forms.Select()
        }
    
