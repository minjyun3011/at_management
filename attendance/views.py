from django.views import generic
from .models import Kid_Information
from .models import Event
from .forms import EventForm
from .forms import CalendarForm
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.template import loader
import json
import time
from django.middleware.csrf import get_token


class IndexView(generic.ListView):
    model = Kid_Information
    template_name = 'attendance/base.html'

def index(request):
    get_token(request)
    template = loader.get_template("attendance/base.html")
    return HttpResponse("template.render()")

@require_http_methods(["POST"])
def add_event(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        event = Event(
            start_time=data['start_time'],
            end_time=data['end_time'],
            full_name=data['full_name'],
            gender=data['gender']
        )
        event.save()
        return JsonResponse({'message': 'Event successfully added'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


@require_http_methods(["POST"])
def get_events(request):
    """
    イベントの取得
    """

    # JSONの解析
    datas = json.loads(request.body)

    # リクエストの取得
    start_time = datas["start_time"]
    end_time = datas["end_time"]

    # 時間に変換。JavaScriptのタイムスタンプはミリ秒なので秒に変換
    formatted_start_time = time.strftime(
        "%H:%M", time.localtime(start_time / 1000))
    formatted_end_time = time.strftime(
        "%H:%M", time.localtime(end_time / 1000))

    # FullCalendarの表示範囲のみ表示
    events = Event.objects.filter(
        start_time__lte=formatted_end_time, end_time__gte=formatted_start_time
    )

    # FullCalendarのための配列で返却
    events_list = []
    for event in events:
        events_list.append(
            {
                "title": f"{event.full_name} {('くん' if event.gender == 'M' else 'ちゃん')}",
                "start": event.start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "end": event.end_time.strftime("%Y-%m-%dT%H:%M:%S"),
            }
        )

    return JsonResponse(events_list, safe=False)
