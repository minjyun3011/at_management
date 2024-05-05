import json
import logging
from datetime import datetime
from .forms import AttendanceInfoForm
from django.views.generic.edit import FormView
from django.http import JsonResponse
from django.views.generic.edit import FormView
from django.urls import reverse, reverse_lazy
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.utils import timezone

from .forms import UserForm, CheckUserForm

from django.views.generic.edit import CreateView
from .models import User, Attendance_info
from django.views.generic import TemplateView
from django.contrib import messages 
from datetime import datetime
from django.shortcuts import get_object_or_404


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
            self.request.session['recipient_number'] = recipient_number
            self.request.session['user_name'] = user.name
            self.request.session['user_gender'] = user.gender
            return redirect(reverse('attendance:home1'))
        else:
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

    #セッションを使用しない場合にのみ有効な処理
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     recipient_number = self.request.session.get('recipient_number')
    #     if recipient_number:
    #         attendance_infos = Attendance_info.objects.filter(user__recipient_number=recipient_number).order_by('-calendar_date')
    #         context['attendance_infos'] = attendance_infos
    #     return context

# class Attendance_TodayView(TemplateView):
#     model = Attendance_info
#     template_name = 'attendance/home1.html'  # 詳細表示用のテンプレート

#     def get_context_data(self, **kwargs):
#         # ビューのコンテキストに追加のデータを挿入するためのメソッド
#         context = super().get_context_data(**kwargs)
#         context['now'] = timezone.now()  # 現在の時刻データを追加
#         return context
    

@require_http_methods(["POST"])
def add_event(request):
    try:
        data = json.loads(request.body)
        logger.debug("Request data: %s", data)

        # セッションから受給者番号を取得して、対応するUserオブジェクトを取得
        recipient_number = request.session.get('recipient_number')
        user = User.objects.get(recipient_number=recipient_number)

        # フォームを初期化し、データをバリデーション
        form = AttendanceInfoForm(data)
        if form.is_valid():
            event = form.save(commit=False)
            user = get_object_or_404(User, pk=request.session.get('recipient_number'))
            event.recipient_number = user  # Userオブジェクトを設定
            event.save()  # イベントを保存

            # イベント追加成功のレスポンスデータ
            response_data = {
                'message': 'Event successfully added',
                'eventData': {
                    'title': f"{event.status} - {event.calendar_date}",
                    'start': datetime.combine(event.calendar_date, event.start_time).isoformat(),
                    'end': datetime.combine(event.calendar_date, event.end_time).isoformat(),
                    'status': event.get_status_display(),
                    'transportation_to': event.get_transportation_to_display(),
                    'transportation_from': event.get_transportation_from_display(),
                    'absence_reason': event.absence_reason or "N/A",
                }
            }
            logger.debug("Event added: %s", response_data)
            return JsonResponse(response_data, status=200)
        else:
            # フォームが無効であればエラーを返す
            logger.debug("Form errors: %s", form.errors)
            return JsonResponse({'errors': form.errors}, status=400)

    except User.DoesNotExist:
        # Userが見つからない場合
        logger.error("User not found with recipient_number: %s", recipient_number)
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        logger.error("Failed to add event: %s", str(e))
        return JsonResponse({'error': 'Internal Server Error', 'message': str(e)}, status=500)


#カレンダー選択後にその日付の中に入っているイベントデータを取得して入力欄に表示しておくために必要な関数
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
            recipient_number=recipient_number,
            calendar_date__range=[start_date, end_date]
        ).values( 'calendar_date', 'start_time', 'end_time', 'status', 'transportation_to', 'transportation_from', 'absence_reason')

        events_data = list(events)  # QuerySetをリストに変換してJSON可能な形式にする

        return JsonResponse(events_data, safe=False)  # リスト形式のレスポンスを許可
    except Exception as e:
        return JsonResponse({'error': 'Internal Server Error', 'message': str(e)}, status=500)
