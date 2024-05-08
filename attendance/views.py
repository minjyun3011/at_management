import json
import logging
from .forms import AttendanceInfoForm
from django.views.generic.edit import FormView
from django.http import JsonResponse
from django.views.generic.edit import FormView
from django.urls import reverse, reverse_lazy
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect

from .forms import UserForm, CheckUserForm

from django.views.generic.edit import CreateView
from .models import User, Attendance_info
from django.views.generic import TemplateView
from django.contrib import messages 
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.utils.dateformat import DateFormat




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
        recipient_number = request.session.get('recipient_number')
        user = get_object_or_404(User, recipient_number=recipient_number)

        form = AttendanceInfoForm(data)
        if form.is_valid():
            event = form.save(commit=False)
            event.recipient_number = user
            event.save()

            # イベントデータをISO 8601形式に整形して返す
            response_data = {
                'message': 'Event successfully added',
                'eventData': {
                    'id': event.id,
                    'calendar_date': event.calendar_date.strftime('%Y-%m-%d'),
                    'start_time': DateFormat(event.start_time).format('c'),  # ISO 8601 format
                    'end_time': DateFormat(event.end_time).format('c'),
                    'status': event.get_status_display(),  # get_status_display() で選択肢の表示用文字列を取得
                    'transportation_to': event.get_transportation_to_display(),  # 同様に表示用文字列を取得
                    'transportation_from': event.get_transportation_from_display(),  # 同様に表示用文字列を取得
                    'absence_reason': event.absence_reason or "N/A",
                }
            }
            return JsonResponse(response_data, status=200)
        else:
            # フォームエラーがあればJSON形式で返す
            return JsonResponse({'errors': form.errors.get_json_data()}, status=400)
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Internal Server Error', 'message': str(e)}, status=500)

#カレンダー選択後にその日付の中に入っているイベントデータを取得して入力欄に表示しておくために必要な関数
@require_http_methods(["POST"])
def get_events(request):
    try:
        calendar_data = json.loads(request.body)
        recipient_number = request.session.get('recipient_number')
        user = User.objects.get(recipient_number=recipient_number)

        # 入力された開始日と終了日を取得
        start_date = parse_datetime(calendar_data.get('start_time')).date()
        end_date = parse_datetime(calendar_data.get('end_time')).date()

        events = Attendance_info.objects.filter(
            recipient_number=user,
            calendar_date__range=[start_date, end_date]
        )

        # イベントデータをISO 8601形式に整形
        events_data = [{
            'id': event.id,
            'calendar_date': event.calendar_date.strftime('%Y-%m-%d'),
            'start_time': DateFormat(event.start_time).format('c'),  # ISO 8601 format
            'end_time': DateFormat(event.end_time).format('c'),
            'status': event.status,
            'transportation_to': event.transportation_to,
            'transportation_from': event.transportation_from,
            'absence_reason': event.absence_reason
        } for event in events]

        return JsonResponse(events_data, safe=False)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'Internal Server Error', 'message': str(e)}, status=500)
