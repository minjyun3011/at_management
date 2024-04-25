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

class HomePageView(TemplateView):
    template_name = 'attendance/home0.html'


class CheckUserView(FormView):
    template_name = 'attendance/home0.html'
    form_class = CheckUserForm

    def form_valid(self, form):
        recipient_number = form.cleaned_data['recipient_number']
        user = User.objects.filter(recipient_number=recipient_number).first()
        
        if user:
            # ユーザーが見つかった場合、ユーザーに関連する出席情報を検索
            attendance_info = Attendance_info.objects.filter(user=user).first()
            if attendance_info:
                # 出席情報が存在する場合はその情報の詳細ページへリダイレクト
                return redirect('attendance:home1', pk=attendance_info.pk)
            else:
                # 出席情報がない場合は適切なエラーメッセージを表示してユーザー登録画面にリダイレクト
                messages.error(self.request, "出席情報が見つかりませんでした。")
                return redirect('attendance:user_registration', pk=user.pk)
        else:
            # ユーザーが見つからない場合はエラーをフォームに追加して同じページに留まる
            messages.error(self.request, "この受給者番号のユーザーは存在しません。")
            return self.form_invalid(form)

    def form_invalid(self, form):
        # フォームが無効の場合は、エラーメッセージを表示するために同じページに戻る
        return super().form_invalid(form)


class UserRegistrationView(CreateView):
    model = User
    form_class = UserForm
    template_name = 'attendance/home0.html'
    success_url = reverse_lazy('attendance:home1')

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)


class Home1View(TemplateView):
    template_name = 'attendance/home1.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.session.get('user_id')  # セッションからユーザーIDを取得
        if user_id:
            user = get_object_or_404(User, pk=user_id)
            context['user'] = user
            context['attendance_infos'] = Attendance_info.objects.filter(user=user).order_by('-date')
        return context


class Attendance_TodayView(TemplateView):
    model = Attendance_info
    template_name = 'attendance/home1.html'  # 詳細表示用のテンプレート

    def get_context_data(self, **kwargs):
        # ビューのコンテキストに追加のデータを挿入するためのメソッド
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()  # 現在の時刻データを追加
        return context
    

@csrf_exempt
@require_http_methods(["POST"])
def add_event(request):
    try:
        data = json.loads(request.body)
        # クライアントからのリクエストにユーザー情報を追加（例えば、ログインしているユーザーのID）
        # この例では、ユーザーがログインしていると仮定しています。適宜調整が必要です。
        data['user'] = request.user.id if hasattr(request.user, 'id') else None

        form = AttendanceInfoForm(data)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user  # ユーザー情報の設定
            event.save()

            # 成功時のデータをクライアントに送信
            return JsonResponse({
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
            }, status=200)
        else:
            # バリデーションエラーの場合、エラー情報を返す
            return JsonResponse({'errors': form.errors}, status=400)
    except Exception as e:
        # 例外が発生した場合、エラーログを記録し、クライアントにはエラーメッセージを返す
        import logging
        logger = logging.getLogger(__name__)
        logger.error("Failed to add event: %s", str(e))
        return JsonResponse({'error': 'Internal Server Error', 'message': str(e)}, status=500)
    
#カレンダー選択後にその日付の元々のイベントデータを取得して入力欄に表示しておくために必要な関数
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Attendance_info


@csrf_exempt
@require_http_methods(["POST"])
def get_events(request):
    try:
        calendar_data = json.loads(request.body)
        start_date_str = calendar_data.get('start_time')
        end_date_str = calendar_data.get('end_time')

        # 文字列からdatetimeオブジェクトに変換
        start_date = parse_datetime(start_date_str)
        end_date = parse_datetime(end_date_str)

        if not (start_date and end_date):
            return JsonResponse({'error': 'Invalid date format'}, status=400)

        # datetimeオブジェクトの日付部分だけを取得
        start_date = start_date.date()
        end_date = end_date.date()

        events = Attendance_info.objects.filter(
            calendar_date__range=[start_date, end_date]
        ).select_related('user')

        events_data = [{
            'calendar_date': event.calendar_date.strftime('%Y-%m-%d'),
            'start': event.start_time.strftime('%H:%M'),
            'end': event.end_time.strftime('%H:%M'),
            'status': event.status,
            'transportation_to': event.transportation_to,
            'transportation_from': event.transportation_from,
            'absence_reason': event.absence_reason
        } for event in events]

        return JsonResponse(events_data, safe=False)
    except Exception as e:
        # エラー内容をログに記録
        import logging
        logger = logging.getLogger(__name__)
        logger.error("Error fetching events: %s", str(e))
        return JsonResponse({'error': 'Internal Server Error', 'message': str(e)}, status=500)
    
# class EventAddView(FormView):
#     template_name = 'attendance/event_add.html'
#     form_class = EventForm
#     success_url = reverse_lazy('home')  # 成功時のリダイレクト先

#     def form_valid(self, form):
#         event = form.save(commit=False)  # フォームのデータをまだデータベースには保存しない
#         event.calendar_date = event.start_time.date()  # 開始時間からカレンダー日付を設定
#         event.save()  # データベースに保存

#         if self.request.is_ajax():
#             # AJAXリクエストの場合はJSONレスポンスを返す
#             data = {
#                 'message': 'Event successfully added',
#                 'event_id': event.id,
#                 'start_time': event.start_time.strftime('%H:%M'),
#                 'end_time': event.end_time.strftime('%H:%M'),
#                 'full_name': event.full_name,
#                 'calendar_date': event.calendar_date.isoformat(),
#             }
#             return JsonResponse(data, status=200)
#         else:
#             # 非AJAXリクエストの場合は指定された成功URLにリダイレクト
#             return super().form_valid(form)

#     def form_invalid(self, form):
#         if self.request.is_ajax():
#             # フォームが無効な場合のAJAXリクエスト処理
#             return JsonResponse(form.errors, status=400)
#         else:
#             # フォームが無効な場合の通常のリクエスト処理
#             return super().form_invalid(form)
        
# ####

# # ロギング設定
# logger = logging.getLogger()  # ルートロガーを取得

# # ログファイルのハンドラーを作成
# file_handler = logging.FileHandler('/Users/satoso/Python/at_management/project/logs/file.log')
# file_handler.setLevel(logging.INFO)  # INFOレベル以上のログを記録

# # コンソールのハンドラーを作成
# stream_handler = logging.StreamHandler()
# stream_handler.setLevel(logging.INFO)  # INFOレベル以上のログをコンソールに出力

# # ロギングフォーマットを設定
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# file_handler.setFormatter(formatter)
# stream_handler.setFormatter(formatter)

# # ロガーにハンドラーを追加
# logger.addHandler(file_handler)
# logger.addHandler(stream_handler)


