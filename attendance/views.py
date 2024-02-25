from django.views import generic
from .models import Kid_Information

class IndexView(generic.ListView):
    model = Kid_Information
    template_name = 'attendance/base.html'
