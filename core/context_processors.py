from django.conf import settings


def support_contact(request):
    return {
        'support_phone': settings.SUPPORT_PHONE,
        'support_whatsapp': settings.SUPPORT_WHATSAPP,
    }
