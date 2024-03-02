from django.views import generic
from django.http import JsonResponse, HttpResponse
from django.template import loader
from django.views.decorators.http import require_http_methods
from .models import Kid_Information, Event
from .forms import EventForm, CalendarForm
import json
import time
from django.middleware.csrf import get_token
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
    if request.method == 'POST':
        data = json.loads(request.body)
        # parse_datetime を使用している場合、フロントエンドからの日付/時刻文字列が適切なフォーマットであることを確認する
        event = Event(
            start_time=parse_datetime(data['start_time']),
            end_time=parse_datetime(data['end_time']),
            full_name=data['full_name'],
            gender=data['gender']
        )
        event.save()
        return JsonResponse({'message': 'Event successfully added'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

@require_http_methods(["POST"])
def get_events(request):
    datas = json.loads(request.body)
    start_time = datas["start_time"]
    end_time = datas["end_time"]

    # 時間に変換。JavaScriptのタイムスタンプはミリ秒なので秒に変換
    formatted_start_time = time.strftime("%H:%M", time.localtime(int(start_time) / 1000))
    formatted_end_time = time.strftime("%H:%M", time.localtime(int(end_time) / 1000))

    # FullCalendarの表示範囲内のイベントのみをフィルタリング
    events = Event.objects.filter(start_time__lte=formatted_end_time, end_time__gte=formatted_start_time)

    # FullCalendarに適した形式でイベントデータを返却
    events_list = []
    for event in events:
        events_list.append({
            "title": f"{event.full_name} {('くん' if event.gender == 'M' else 'ちゃん')}",
            "start": event.start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "end": event.end_time.strftime("%Y-%m-%dT%H:%M:%S"),
        })

    return JsonResponse(events_list, safe=False)
