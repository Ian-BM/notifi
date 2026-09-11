from django.urls import path

from apps.dashboard.views import admin_dashboard

from . import views

app_name = 'schools'

urlpatterns = [
    path('', admin_dashboard, name='admin_index'),
    path('schools/', views.schools_list, name='schools_list'),
    path('schools/add/', views.school_add, name='school_add'),
    path('schools/<int:pk>/edit/', views.school_edit, name='school_edit'),
    path('schools/<int:pk>/topup/', views.school_topup, name='school_topup'),
    path('transactions/', views.transactions_list, name='transactions_list'),
    path('beem-test/', views.beem_test_panel, name='beem_test'),
    path('beem-test/send/', views.beem_test_send, name='beem_test_send'),
    path('beem-test/balance/', views.beem_test_balance, name='beem_test_balance'),
]
