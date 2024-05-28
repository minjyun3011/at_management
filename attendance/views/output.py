from django.shortcuts import render
from django.views import View
from attendance.models import Attendance_info  # モデル名を修正
from django.http import JsonResponse
from datetime import datetime

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
                        'absence_reason': info.absence_reason  # 欠席理由
                    })
            except ValueError:
                return JsonResponse({'error': 'Invalid date format'}, status=400)

        context = {
            'combined_data': combined_data,
            'selected_date': selected_date,
        }

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(context)
        else:
            return render(request, self.template_name, context)
