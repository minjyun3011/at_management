from django.views import generic
from django.http import JsonResponse, HttpResponse
from django.template import loader
from django.views.decorators.http import require_http_methods
from .models import Kid_Information, Event
from .forms import EventForm
import json
import time
from django.middleware.csrf import get_token
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
import logging
from django.utils.dateparse import parse_datetime



class IndexView(generic.ListView):
    model = Kid_Information
    template_name = 'attendance/base.html'

def index(request):
    get_token(request)
    template = loader.get_template("attendance/base.html")
    return HttpResponse(template.render({}, request))

@require_http_methods(["POST"])
def add_event(request):
    # HTTPリクエストの本文からデータを取得する
    data = json.loads(request.body)
    form = EventForm(data)
    
    if form.is_valid():
        event = form.save(commit=False)
        
        # カレンダーの日付を設定
        event.calendar_date = event.start_time.date()
        
        event.save()
        
        return JsonResponse({
            'message': 'Event successfully added',
            'event_id': event.id
        }, status=200)
    else:
        return JsonResponse({'errors': form.errors}, status=400)
    from django.utils.dateparse import parse_datetime

@csrf_exempt
@require_http_methods(["POST"])
def get_events(request):
    try:
        datas = json.loads(request.body)
        start_time_str = datas.get("start_time")
        end_time_str = datas.get("end_time")

        # 文字列をdatetimeオブジェクトに変換
        start_time = parse_datetime(start_time_str)
        end_time = parse_datetime(end_time_str)

        if not start_time or not end_time:
            raise ValueError("Invalid start_time or end_time format")

        # FullCalendarの表示範囲内のイベントのみをフィルタリング
        events = Event.objects.filter(start_time__lte=end_time, end_time__gte=start_time)

        # FullCalendarに適した形式でイベントデータを返却
        events_list = []
        for event in events:
            events_list.append({
                "title": f"{event.full_name} {('くん' if event.gender == 'M' else 'ちゃん')}",
                "start": event.start_time.isoformat(),
                "end": event.end_time.isoformat(),
            })

        return JsonResponse(events_list, safe=False)
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
