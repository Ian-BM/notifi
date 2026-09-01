from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLES = [('admin', 'Platform Admin'), ('school', 'School Admin')]

    role = models.CharField(max_length=20, choices=ROLES, default='school')
    school = models.ForeignKey(
        'schools.School',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='users'
    )
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_platform_admin(self):
        return self.role == 'admin'

    def is_school_admin(self):
        return self.role == 'school'

    class Meta:
        db_table = 'notifi_users'


class OnboardingProgress(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='onboarding'
    )
    completed = models.BooleanField(default=False)
    step_welcome_done = models.BooleanField(default=False)
    step_contacts_done = models.BooleanField(default=False)
    step_sms_done = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def completion_percentage(self):
        steps = [
            self.step_welcome_done,
            self.step_contacts_done,
            self.step_sms_done,
        ]
        done = sum(1 for s in steps if s)
        return int((done / len(steps)) * 100)

    def all_done(self):
        return all([
            self.step_welcome_done,
            self.step_contacts_done,
            self.step_sms_done,
        ])

    def __str__(self):
        return f"Onboarding — {self.user.username}"

    class Meta:
        db_table = 'notifi_onboarding_progress'
