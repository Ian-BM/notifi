from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from apps.messaging.views import sms_callback
from core.views import landing_page, pricing_page

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', landing_page, name='landing'),
    path('pricing/', pricing_page, name='pricing'),
    path('', include('apps.accounts.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('contacts/', include('apps.contacts.urls')),
    path('', include('apps.messaging.urls')),
    path('admin-panel/', include('apps.schools.urls')),
    path('api/sms/callback/', sms_callback, name='sms_callback'),

    # SEO files
    path('robots.txt', TemplateView.as_view(
        template_name='robots.txt', content_type='text/plain'
    )),
    path('sitemap.xml', TemplateView.as_view(
        template_name='sitemap.xml', content_type='application/xml'
    )),
]
