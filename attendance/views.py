from django.views import generic
from .models import Kid_Information
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

class IndexView(generic.ListView):
    model = Kid_Information
    template_name = 'attendance/base.html'

def index(request):
    template = loader.get_template("attendance/base.html")
    return HttpResponse("template.render()")
