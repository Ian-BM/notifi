from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import OnboardingProgress


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_onboarding_progress(sender, instance, created, **kwargs):
    if created:
        OnboardingProgress.objects.get_or_create(user=instance)
