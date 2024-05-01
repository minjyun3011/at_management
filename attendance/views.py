import re
import json
import logging
from datetime import datetime
from django import forms
from .forms import AttendanceInfoForm
from django.views.generic.edit import FormView
from django.http import JsonResponse, HttpResponse
from django.template import loader
from django.views.generic import ListView
from django.views.generic.edit import FormView
from django.urls import reverse, reverse_lazy
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers import serialize
from django.shortcuts import render, redirect, get_object_or_404
from django.middleware.csrf import get_token
from .models import Kid_Information, Event
from django.utils import timezone

from .forms import UserForm, CheckUserForm

from django.urls import path, include

from django.views.generic.edit import CreateView
from .models import User, Attendance_info
from django.views.generic import TemplateView
from django.contrib import messages 
from django.contrib.auth import get_user_model  # この行を追加
from django.contrib.auth import login, authenticate
logger = logging.getLogger(__name__)

class HomePageView(TemplateView):
    template_name = 'attendance/home0.html'

# 受給者番号の入力でログインするパターン（２回目以降）
class CheckUserView(FormView):
    template_name = 'attendance/home0.html'
    form_class = CheckUserForm

    def form_valid(self, form):
        recipient_number = form.cleaned_data['recipient_number']
        user = User.objects.filter(recipient_number=recipient_number).first()

        if user:
            self.request.session.modified = True
            self.request.session['user_id'] = user.pk
            # recipient_number をセッションに保存
            self.request.session['recipient_number'] = recipient_number
            return redirect(reverse('attendance:home1'))
        else:
            # ユーザーが見つからない場合はエラーメッセージを設定して同じページに留まる
            messages.error(self.request, "正確な受給者番号を入力してください。")
            return self.form_invalid(form)

    def form_invalid(self, form):
        # フォームが無効の場合は、エラーメッセージを設定して同じページに戻る
        return super().form_invalid(form)


class UserRegistrationView(CreateView):
    model = User
    form_class = UserForm
    template_name = 'attendance/home0.html'
    success_url = reverse_lazy('attendance:home1')

    def form_valid(self, form):
        recipient_number = form.cleaned_data.get('recipient_number')
        if User.objects.filter(recipient_number=recipient_number).exists():
            logger.debug("User with this recipient number already exists.")
            form.add_error(None, 'この受給者番号のユーザーは既に存在しています。')
            return self.form_invalid(form)
        else:
            logger.debug("No existing user, creating new user")
            self.object = form.save()
            logger.debug(f"New user {self.object.name} created and saved.")
            return redirect(self.get_success_url())

    def form_invalid(self, form):
        # Form invalidのログを記録
        logger.debug(f"Form invalid, errors: {form.errors}")
        return super().form_invalid(form)

#home0.htmlからのリダイレクト直後の処理内容
class Home1View(TemplateView):
    template_name = 'attendance/home1.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipient_number = self.request.session.get('recipient_number')
        if recipient_number:
            attendance_infos = Attendance_info.objects.filter(user__recipient_number=recipient_number).order_by('-calendar_date')
            context['attendance_infos'] = attendance_infos
        return context



class Attendance_TodayView(TemplateView):
    model = Attendance_info
    template_name = 'attendance/home1.html'  # 詳細表示用のテンプレート

    def get_context_data(self, **kwargs):
        # ビューのコンテキストに追加のデータを挿入するためのメソッド
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()  # 現在の時刻データを追加
        return context
    
# ロガーの設定
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@csrf_exempt
@require_http_methods(["POST"])
def add_event(request):
    try:
        data = json.loads(request.body)
        logger.debug("Request data: %s", data)

        # フォームのデータにユーザー名を追加
        data['user'] = request.user.username

        form = AttendanceInfoForm(data)
        logger.debug("Form valid: %s", form.is_valid())
        if form.errors:
            logger.debug("Form errors: %s", form.errors)

        if form.is_valid():
            event = form.save()

            response_data = {
                'message': 'Event successfully added',
                'eventData': {
                    'id': event.id,
                    'title': f"{event.status} - {event.calendar_date}",
                    'start': datetime.datetime.combine(event.calendar_date, event.start_time).isoformat(),
                    'end': datetime.datetime.combine(event.calendar_date, event.end_time).isoformat(),
                    'status': event.get_status_display(),
                    'transportation_to': event.get_transportation_to_display(),
                    'transportation_from': event.get_transportation_from_display(),
                    'absence_reason': event.absence_reason or "N/A",
                }
            }
            logger.debug("Event added: %s", response_data)
            return JsonResponse(response_data, status=200)
        else:
            return JsonResponse({'errors': form.errors}, status=400)

    except Exception as e:
        logger.error("Failed to add event: %s", str(e))
        return JsonResponse({'error': 'Internal Server Error', 'message': str(e)}, status=500)


#カレンダー選択後にその日付の中に入っているイベントデータを取得して入力欄に表示しておくために必要な関数
@csrf_exempt
@require_http_methods(["POST"])
def get_events(request):
    try:
        calendar_data = json.loads(request.body)
        recipient_number = request.session.get('recipient_number')
        #セッションに保存されているrecipient_numberが本当にUserモデルのものなのか照合
        user = User.objects.get(recipient_number=recipient_number)

        # 入力された開始日と終了日を取得
        start_date_str = calendar_data.get('start_time')
        end_date_str = calendar_data.get('end_time')

        # 文字列からdatetimeオブジェクトに変換し、日付の部分だけを抽出
        start_date = parse_datetime(start_date_str).date()
        end_date = parse_datetime(end_date_str).date()

        events = Attendance_info.objects.filter(
            user=user,
            calendar_date__range=[start_date, end_date]
        ).values('id', 'calendar_date', 'start_time', 'end_time', 'status', 'transportation_to', 'transportation_from', 'absence_reason')

        events_data = list(events)  # QuerySetをリストに変換してJSON可能な形式にする

        return JsonResponse(events_data, safe=False)  # リスト形式のレスポンスを許可
    except Exception as e:
        return JsonResponse({'error': 'Internal Server Error', 'message': str(e)}, status=500)
