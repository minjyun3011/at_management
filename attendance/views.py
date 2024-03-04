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



class IndexView(generic.ListView):
    model = Kid_Information
    template_name = 'attendance/base.html'

def index(request):
    get_token(request)
    template = loader.get_template("attendance/base.html")
    return HttpResponse(template.render({}, request))


@require_http_methods(["POST"])
def add_event(request):
    # リクエストからJSONデータを読み込む
    data = json.loads(request.body)
    
    # EventFormをインスタンス化し、送信されたデータで初期化
    form = EventForm(data)
    
    # フォームのバリデーションを実行
    if form.is_valid():
        # フォームのデータが有効であれば、フォームからモデルインスタンスを保存
        event = form.save()
        
        # 成功レスポンスを返す
        return JsonResponse({
            'message': 'Event successfully added',
            'event_id': event.id  # イベントIDを含むメッセージを返す（フロントエンドで何らかの用途に使用する場合）
        }, status=200)
    else:
        # フォームのバリデーションに失敗した場合は、エラーメッセージを返す
        return JsonResponse({'errors': form.errors}, status=400)
    from django.utils.dateparse import parse_datetime

@csrf_exempt
@require_http_methods(["POST"])
def get_events(request):
    datas = json.loads(request.body)
    start_time = parse_datetime(datas["start_time"])
    end_time = parse_datetime(datas["end_time"])

    # FullCalendarの表示範囲内のイベントのみをフィルタリング
    events = Event.objects.filter(start_time__lte=end_time, end_time__gte=start_time)

    # FullCalendarに適した形式でイベントデータを返却
    events_list = []
    for event in events:
        events_list.append({
            "title": f"{event.full_name} {('くん' if event.gender == 'M' else 'ちゃん')}",
            "start": event.start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "end": event.end_time.strftime("%Y-%m-%dT%H:%M:%S"),
        })

    return JsonResponse(events_list, safe=False)



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
