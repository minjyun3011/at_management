import re
import json
import logging
from datetime import datetime
from django import forms
from .forms import EventForm
from django.views.generic.edit import FormView
from django.http import JsonResponse, HttpResponse
from django.template import loader
from django.views.generic import ListView
from django.views.generic.edit import FormView
from django.urls import reverse, reverse_lazy  # reverse_lazy を追加
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers import serialize
from django.shortcuts import render, redirect
from django.middleware.csrf import get_token
from .models import Kid_Information, Event
from django.utils import timezone


from django.views.generic.detail import DetailView


from .forms import UserForm,  CheckUserForm

from django.urls import path, include

from django.views.generic.edit import CreateView
from .models import User, Attendance_info
from django.views.generic import TemplateView

class HomePageView(CreateView):
    model = User
    form_class = UserForm
    template_name = 'attendance/home0.html'
    success_url = reverse_lazy('attendance:home1')  # home1 へのリダイレクト

    # def get_success_url(self):
    #     # 新しく作成されたユーザーのIDをURLに含める
    #     return reverse('attendance:attendance-detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        # フォームデータが有効であれば保存し、get_success_urlで定義されたURLにリダイレクト
        return super().form_valid(form)
    


class CheckUserView(FormView):
    template_name = 'attendance/home0.html'
    form_class = CheckUserForm  # 受給者番号をチェックするフォームクラス

    def form_valid(self, form):
        recipient_number = form.cleaned_data['recipient_number_login']
        try:
            user = User.objects.get(recipient_number=recipient_number)
            attendance_info = Attendance_info.objects.filter(user=user).first()
            if attendance_info:
                return redirect('attendance:attendance_detail', pk=attendance_info.pk)
            else:
                # 関連する出欠情報がない場合、ユーザー登録画面にリダイレクト
                return redirect('attendance:register', pk=user.pk)
        except User.DoesNotExist:
            form.add_error(None, "この受給者番号のユーザーは存在しません。")
            return self.form_invalid(form)

class UserRegistrationView(FormView):
    model = User
    form_class = UserForm
    template_name = 'attendance/home0.html'
    success_url = reverse_lazy('attendance:home')  # 適切なリダイレクト先を設定

    def form_valid(self, form):
        user = form.save()
        # 新しくユーザーを登録した後、該当ユーザーの出欠情報画面にリダイレクト
        return redirect('attendance:attendance_detail', pk=user.pk)

class Home1View(TemplateView):
    template_name = 'attendance/home1.html'

# class Attendance_TodayView(DetailView):
#     model = Attendance_info
#     template_name = 'attendance/home1.html'  # 詳細表示用のテンプレート

#     def get_context_data(self, **kwargs):
#         # ビューのコンテキストに追加のデータを挿入するためのメソッド
#         context = super().get_context_data(**kwargs)
#         context['now'] = timezone.now()  # 現在の時刻データを追加
#         return context
    
# @require_http_methods(["POST"])
# def add_event(request):
#     data = json.loads(request.body)
#     form = EventForm(data)

#     if form.is_valid():
#         event = form.save(commit=False)
        
#         # カレンダーの日付を設定
#         event.calendar_date = event.start_time.date()

#         # 保存
#         event.save()

#         # 成功時のレスポンス
#         return JsonResponse({
#             'message': 'Event successfully added',
#             'event_id': event.id,
#             'start_time': event.start_time.strftime('%H:%M'),  # 開始時間を文字列で返す
#             'end_time': event.end_time.strftime('%H:%M'),      # 終了時間を文字列で返す
#             'full_name': event.full_name,
#             'calendar_date': event.calendar_date,  # カレンダーの日付を文字列で返す
#         }, status=200)
#     else:
#         # バリデーションエラーの場合
#         errors = form.errors.get_json_data()
#         return JsonResponse({'errors': errors}, status=400)
    
# @csrf_exempt
# @require_http_methods(["POST"])
# def get_events(request):
#     try:
#         data = json.loads(request.body)
#         start_time_str = data.get("start_time")
#         end_time_str = data.get("end_time")

#         if not isinstance(start_time_str, str) or not isinstance(end_time_str, str):
#             return JsonResponse({'error': 'start_time and end_time must be strings'}, status=400)

#         # ログ出力でデータ形式を確認
#         logging.info(f"Start time: {start_time_str}, End time: {end_time_str}")

#         # パースしてみる（エラーがあればキャッチされる）
#         start_time = parse_datetime(start_time_str)
#         end_time = parse_datetime(end_time_str)

#         if start_time is None or end_time is None:
#             raise ValueError("Invalid date format")

#         # ここにイベントを取得するロジックを追加

#         return JsonResponse({'message': 'Events fetched successfully'})
#     except Exception as e:
#         logging.error(f"Error fetching events: {str(e)}")
#         return JsonResponse({'error': 'Failed to fetch events'}, status=500)
    

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


