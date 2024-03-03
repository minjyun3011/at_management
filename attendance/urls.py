from django.urls import path, include
from . import views

app_name = "attendance"

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('api/events/', views.add_event, name='add_event'),
    ]
