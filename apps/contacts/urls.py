from django.urls import path

from . import views

app_name = 'contacts'

urlpatterns = [
    path('', views.contacts_list, name='contacts_list'),
    path('add/', views.contact_add, name='contact_add'),
    path('delete/<int:pk>/', views.contact_delete, name='contact_delete'),
    path('import/', views.contacts_import, name='contacts_import'),
    path('groups/', views.groups_list, name='groups_list'),
    path('groups/add/', views.group_add, name='group_add'),
]
