import json
import logging
from ..forms import AttendanceInfoForm
from django.views.generic.edit import FormView
from django.http import JsonResponse
from django.views.generic.edit import FormView
from django.urls import reverse, reverse_lazy
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect

from ..forms import UserForm, CheckUserForm

from django.views.generic.edit import CreateView
from ..models import User, Attendance_info
from django.views.generic import TemplateView
from django.contrib import messages 
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.utils.dateformat import DateFormat

from django.core.exceptions import ObjectDoesNotExist
from datetime import date, time,timedelta




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
            
            # 新規ユーザー登録後にセッションを設定
            self.request.session['recipient_number'] = recipient_number
            self.request.session['user_name'] = self.object.name
            self.request.session['user_gender'] = self.object.gender
            
            return redirect(self.get_success_url())

    def form_invalid(self, form):
        # Form invalidのログを記録
        logger.debug(f"Form invalid, errors: {form.errors}")
        return super().form_invalid(form)


#home0.htmlからのリダイレクト直後の処理内容
class Home1View(TemplateView):
    template_name = 'attendance/home1.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipient_number = self.request.session.get('recipient_number')
        today = date.today()

        if recipient_number:
            user = get_object_or_404(User, recipient_number=recipient_number)
            attendance = Attendance_info.objects.filter(recipient_number=user, calendar_date=today).first()
            context['attendance'] = attendance
            context['today'] = today
        return context

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

            response_data = {
                'message': 'Event successfully added',
                'eventData': {
                    'id': event.id,
                    'calendar_date': event.calendar_date.strftime('%Y-%m-%d'),
                    'start_time': DateFormat(event.start_time).format('c') if event.start_time else None,
                    'end_time': DateFormat(event.end_time).format('c') if event.end_time else None,
                    'status': event.get_status_display(),
                    'transportation_to': event.get_transportation_to_display(),
                    'transportation_from': event.get_transportation_from_display(),
                    'absence_reason': event.absence_reason or "N/A",
                }
            }
            return JsonResponse(response_data, status=200)
        else:
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
            'recipient_number': event.recipient_number.recipient_number,
            'calendar_date': event.calendar_date.strftime('%Y-%m-%d'),
            'start_time': event.start_time.strftime('%H:%M:%S') if event.start_time else None,
            'end_time': event.end_time.strftime('%H:%M:%S') if event.end_time else None,
            'status': event.status,
            'transportation_to': event.transportation_to,
            'transportation_from': event.transportation_from,
            'absence_reason': event.absence_reason
        } for event in events]

        return JsonResponse(events_data, safe=False)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        print(f'Unexpected error: {str(e)}')
        return JsonResponse({'error': 'Internal Server Error', 'message': str(e)}, status=500)
    


@require_http_methods(["GET"])
def get_event_details(request):
    date = request.GET.get('date')
    recipient_number = request.GET.get('recipient_number')
    
    if not date or not recipient_number:
        logger.error('Missing required parameters')  # エラーログ
        return JsonResponse({'error': 'Missing required parameters'}, status=400)

    try:
        user = get_object_or_404(User, recipient_number=recipient_number)
        logger.debug(f'User found: {user}')  # ユーザー情報のログ
        try:
            events = Attendance_info.objects.filter(recipient_number=user, calendar_date=date)
            logger.debug(f'Queried events: {events}')  # クエリ結果をログに記録
            combined_data = []

            for event in events:
                is_late_change = False
                current_time = datetime.now()
                event_date = datetime.strptime(date, '%Y-%m-%d').date()
                cutoff_time = datetime.combine(event_date, time(17, 0)) - timedelta(days=1)  # 前日の17時

                if current_time > cutoff_time and event.status == 'AB':
                    is_late_change = True

                combined_data.append({
                    'calendar_date': event.calendar_date.strftime('%Y-%m-%d'),
                    'start_time': event.start_time.strftime('%H:%M') if event.start_time else None,
                    'end_time': event.end_time.strftime('%H:%M') if event.end_time else None,
                    'status': event.status,
                    'transportation_to': event.transportation_to,
                    'transportation_from': event.transportation_from,
                    'absence_reason': event.absence_reason or "",
                    'updated_at': event.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'is_late_change': is_late_change,
                    'name': event.recipient_number.name,
                    'original_status': event.status  # 元の出席データの状態
                })

            if not combined_data:
                logger.warning(f'No events found for date: {date} and recipient_number: {recipient_number}')  # 警告ログ
                return JsonResponse({'message': 'Event not found'}, status=204)

            logger.debug(f'Combined data: {combined_data}')  # 結合データをログに記録
            return JsonResponse({'combined_data': combined_data, 'selected_date': date}, status=200)
        except Attendance_info.DoesNotExist:
            logger.warning(f'No events found for date: {date} and recipient_number: {recipient_number}')  # 警告ログ
            return JsonResponse({'message': 'Event not found'}, status=204)
    except User.DoesNotExist:
        logger.error(f'User not found with recipient_number: {recipient_number}')  # エラーログ
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        logger.error(f'Unexpected error: {str(e)}')  # エラーログ
        return JsonResponse({'error': 'Internal Server Error', 'message': str(e)}, status=500)

@require_http_methods(["POST"])
def edit_event(request):
    try:
        data = json.loads(request.body)
        recipient_number = data.get('recipient_number')
        user = get_object_or_404(User, recipient_number=recipient_number)
        
        event = Attendance_info.objects.get(recipient_number=user, calendar_date=data.get('calendar_date'))

        form = AttendanceInfoForm(data, instance=event)
        if form.is_valid():
            updated_event = form.save()
            is_late_change = False
            current_time = datetime.now()
            event_date = updated_event.calendar_date
            cutoff_time = datetime.combine(event_date, time(17, 0)) - timedelta(days=1)  # 前日の17時
            
            if current_time > cutoff_time and updated_event.status == 'AB':
                is_late_change = True
            
            response_data = {
                'recipient_number': recipient_number,
                'calendar_date': updated_event.calendar_date.strftime('%Y-%m-%d'),
                'start_time': updated_event.start_time.strftime('%H:%M') if updated_event.start_time else None,
                'end_time': updated_event.end_time.strftime('%H:%M') if updated_event.end_time else None,
                'status': updated_event.status,
                'transportation_to': updated_event.transportation_to,
                'transportation_from': updated_event.transportation_from,
                'absence_reason': updated_event.absence_reason or "",
                'updated_at': updated_event.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'is_late_change': is_late_change
            }
            return JsonResponse({'message': 'Event updated successfully', 'eventData': response_data}, status=200)
        else:
            return JsonResponse({'errors': form.errors.get_json_data()}, status=400)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Attendance_info.DoesNotExist:
        return JsonResponse({'error': 'Event not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'Internal Server Error', 'message': str(e)}, status=500)
