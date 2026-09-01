from django.db import models

from apps.schools.models import School
from apps.contacts.models import ContactGroup


class MessageTemplate(models.Model):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE,
        null=True, blank=True, related_name='templates'
    )
    name = models.CharField(max_length=100)
    content = models.TextField()
    is_global = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'notifi_templates'


class Message(models.Model):
    STATUS = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('partial', 'Partially Sent'),
    ]
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name='messages'
    )
    content = models.TextField()
    sender_id_used = models.CharField(max_length=20)
    group = models.ForeignKey(
        ContactGroup, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    group_name_snapshot = models.CharField(max_length=100)
    recipient_count = models.IntegerField(default=0)
    delivered_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    credits_used = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    beem_request_id = models.CharField(max_length=100, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    def delivery_rate(self):
        if self.recipient_count == 0:
            return 0
        return round((self.delivered_count / self.recipient_count) * 100)

    def __str__(self):
        return f"{self.school.name} — {self.sent_at.date()} — {self.recipient_count} recipients"

    class Meta:
        db_table = 'notifi_messages'
        ordering = ['-sent_at']


class Transaction(models.Model):
    TYPES = [
        ('credit_added', 'Credits Added'),
        ('sms_sent', 'SMS Sent'),
        ('payment_received', 'Payment Received'),
    ]
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name='transactions'
    )
    type = models.CharField(max_length=30, choices=TYPES)
    amount = models.IntegerField()
    balance_before = models.IntegerField()
    balance_after = models.IntegerField()
    description = models.CharField(max_length=255)
    reference = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifi_transactions'
        ordering = ['-created_at']
