from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('school/', views.school_dashboard, name='school_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
]
