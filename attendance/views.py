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

class IndexView(ListView):
    model = Kid_Information
    template_name = 'attendance/base.html'

def index(request):
    get_token(request)
    template = loader.get_template("attendance/base.html")
    return HttpResponse(template.render({}, request))

@require_http_methods(["POST"])
def add_event(request):
    data = json.loads(request.body)
    form = EventForm(data)
    
    if form.is_valid():
        event = form.save(commit=False)
        
        # カレンダーの日付を設定
        event.calendar_date = event.start_time.date().strftime('%Y-%m-%d')
        
        event.save()
        
        return JsonResponse({
            'message': 'Event successfully added',
            'event_id': event.id
        }, status=200)
    else:
        print(form.errors)
        return JsonResponse({'errors': form.errors}, status=400)

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

# ログハンドラーをクローズ
file_handler.close()
stream_handler.close()
