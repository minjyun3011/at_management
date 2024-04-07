import re
import json
import logging
from django import forms
from django.http import JsonResponse, HttpResponse
from django.template import loader
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
from .models import Kid_Information, Event
from .forms import EventForm
from django.middleware.csrf import get_token
from datetime import datetime
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.serializers import serialize



class IndexView(ListView):
    model = Kid_Information
    template_name = 'attendance/base.html'
    def index(request):
        get_token(request)
        template = loader.get_template("attendance/base.html")
        return HttpResponse(template.render({}, request))
    
    def get_queryset(self):
        # ここで必要な子供の情報を取得
        return Kid_Information.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # カレンダーに表示するイベントデータを追加
        context['events'] = Event.objects.all()
        return context
    
    def my_view(request):
        events_json = serialize('json', Event.objects.all())
        return render(request, 'attendance:index', {'events': events_json})

@require_http_methods(["POST"])
def add_event(request):
    data = json.loads(request.body)
    form = EventForm(data)

    if form.is_valid():
        event = form.save(commit=False)
        
        # カレンダーの日付を設定
        event.calendar_date = event.start_time.date()

        # 保存
        event.save()

        # 成功時のレスポンス
        return JsonResponse({
            'message': 'Event successfully added',
            'event_id': event.id,
            'start_time': event.start_time.strftime('%H:%M'),  # 開始時間を文字列で返す
            'end_time': event.end_time.strftime('%H:%M'),      # 終了時間を文字列で返す
            'full_name': event.full_name,
            'calendar_date': event.calendar_date,  # カレンダーの日付を文字列で返す
        }, status=200)
    else:
        # バリデーションエラーの場合
        errors = form.errors.get_json_data()
        return JsonResponse({'errors': errors}, status=400)
    
@csrf_exempt
@require_http_methods(["POST"])
def get_events(request):
    try:
        data = json.loads(request.body)
        start_time_str = data.get("start_time")
        end_time_str = data.get("end_time")

        if not isinstance(start_time_str, str) or not isinstance(end_time_str, str):
            return JsonResponse({'error': 'start_time and end_time must be strings'}, status=400)

        # ログ出力でデータ形式を確認
        logging.info(f"Start time: {start_time_str}, End time: {end_time_str}")

        # パースしてみる（エラーがあればキャッチされる）
        start_time = parse_datetime(start_time_str)
        end_time = parse_datetime(end_time_str)

        if start_time is None or end_time is None:
            raise ValueError("Invalid date format")

        # ここにイベントを取得するロジックを追加

        return JsonResponse({'message': 'Events fetched successfully'})
    except Exception as e:
        logging.error(f"Error fetching events: {str(e)}")
        return JsonResponse({'error': 'Failed to fetch events'}, status=500)
    

def event_add(request):
    print("Request received with method:", request.method)  # リクエストメソッドを出力
    if request.method == 'POST':
        print("Processing POST request")
        # AJAXリクエストの場合
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            print("Detected AJAX POST request")
            try:
                data = json.loads(request.body)
                print("Request body loaded:", data)
            except json.JSONDecodeError as e:
                print("Error decoding JSON:", e)
                return HttpResponse(status=400, content='Invalid JSON')

            form = EventForm(data)
            if form.is_valid():
                event = form.save(commit=False)
                event.calendar_date = event.start_time.date()
                event.save()
                print("Event saved:", event.id)  # 保存されたイベントIDを出力
                return JsonResponse({
                    'message': 'Event successfully added',
                    'event_id': event.id,
                    'start_time': event.start_time.strftime('%H:%M'),
                    'end_time': event.end_time.strftime('%H:%M'),
                    'full_name': event.full_name,
                    'calendar_date': event.calendar_date,
                }, status=200)
                
            else:
                # バリデーションエラーの場合
                errors = form.errors.get_json_data()
                print("Form validation errors:", errors)  # バリデーションエラーを出力
                return JsonResponse({'errors': errors}, status=400)
        else:
            print("Detected non-AJAX POST request")
            form = EventForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('attendance:index')
            else:
                return render(request, 'attendance/event_add.html', {'form': form})
    else:
        # GETリクエストの場合
        print("Processing GET request")
        form = EventForm()
        return render(request, 'attendance/event_add.html', {'form': form})
    
# ロギング設定
logger = logging.getLogger()  # ルートロガーを取得

# ログファイルのハンドラーを作成
file_handler = logging.FileHandler('/Users/satoso/Python/at_management/project/logs/file.log')
file_handler.setLevel(logging.INFO)  # INFOレベル以上のログを記録

# コンソールのハンドラーを作成
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)  # INFOレベル以上のログをコンソールに出力

# ロギングフォーマットを設定
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# ロガーにハンドラーを追加
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


