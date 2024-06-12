from django.shortcuts import render
from django.views import View
from attendance.models import Attendance_info, ServiceTime
from django.http import JsonResponse
from datetime import datetime
import logging
from django.shortcuts import render, redirect
from attendance.forms import ServiceTimeForm

logger = logging.getLogger(__name__)


class CombinedAttendanceView(View):
    template_name = 'output/output_menu.html'

    def get(self, request):
        selected_date = request.GET.get('date')
        combined_data = []

        if selected_date:
            try:
                date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
                attendance_infos = Attendance_info.objects.filter(calendar_date=date_obj)

                for info in attendance_infos:
                    combined_data.append({
                        'name': info.recipient_number.name,  # 名前
                        'start_time': str(info.start_time),
                        'end_time': str(info.end_time),
                        'status': info.status,
                        'transportation_to': info.transportation_to,  # 送迎サービス（往路）
                        'transportation_from': info.transportation_from,  # 送迎サービス（復路）
                        'absence_reason': info.absence_reason,  # 欠席理由
                        'updater': info.updater,  # 更新者
                        'updated_at': info.updated_at.isoformat()  # 更新日時
                    })
            except ValueError:
                return JsonResponse({'error': 'Invalid date format'}, status=400)

        context = {
            'combined_data': combined_data,
            'selected_date': selected_date,
        }
        logger.debug(f'Context for response: {context}')

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(context)
        else:
            return render(request, self.template_name, context)


class DailyReportView(View):
    template_name = 'output/reports.html'
    def get(self, request):
        # 必要なデータの取得と処理をここに追加
        context = {}
        return render(request, self.template_name, context)

class SettingView(View):
    template_name = 'output/setting.html'

    def get(self, request):
        form = ServiceTimeForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = ServiceTimeForm(request.POST)
        if form.is_valid():
            # フォームデータを保存
            for day in form.WEEKDAYS:
                for service in form.SERVICE_TYPES:
                    start_time = form.cleaned_data.get(f"{day[0]}_{service[0]}_start")
                    end_time = form.cleaned_data.get(f"{day[0]}_{service[0]}_end")
                    if start_time and end_time:
                        ServiceTime.objects.update_or_create(
                            weekday=day[0],
                            service_type=service[0],
                            defaults={'start_time': start_time, 'end_time': end_time}
                        )
            return redirect('success')  # 成功ページまたは同じ設定ページにリダイレクト
        return render(request, self.template_name, {'form': form})
