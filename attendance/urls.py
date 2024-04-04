from django.urls import path, include
from . import views

app_name = "attendance"

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('api/add_event/', views.add_event, name='add_event'),
    path('api/get_events/', views.get_events, name='get_events'),
    path('api/event_add/', views.event_add, name='event_add'),
    ]
