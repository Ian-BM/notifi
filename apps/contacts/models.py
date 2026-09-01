from django.db import models

from apps.schools.models import School


class ContactGroup(models.Model):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name='groups'
    )
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def contact_count(self):
        return self.contacts.count()

    def __str__(self):
        return f"{self.school.name} — {self.name}"

    class Meta:
        db_table = 'notifi_contact_groups'
        unique_together = ['school', 'name']


class Contact(models.Model):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name='contacts'
    )
    group = models.ForeignKey(
        ContactGroup, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='contacts'
    )
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.phone})"

    class Meta:
        db_table = 'notifi_contacts'
        unique_together = ['school', 'phone']
