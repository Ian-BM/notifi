from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from apps.messaging.views import sms_callback

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
    path('', include('apps.accounts.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('contacts/', include('apps.contacts.urls')),
    path('', include('apps.messaging.urls')),
    path('admin-panel/', include('apps.schools.urls')),
    path('api/sms/callback/', sms_callback, name='sms_callback'),
]
