from django.urls import path

from . import views

app_name = 'messaging'

urlpatterns = [
    path('send-sms/', views.send_sms, name='send_sms'),
    path('send-sms/submit/', views.send_sms_submit, name='send_sms_submit'),
    path('templates/', views.templates_list, name='templates_list'),
    path('templates/add/', views.template_add, name='template_add'),
    path('templates/delete/<int:pk>/', views.template_delete, name='template_delete'),
    path('reports/', views.reports, name='reports'),
]
