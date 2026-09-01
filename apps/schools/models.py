from django.db import models


class School(models.Model):
    SENDER_STATUS = [
        ('none', 'Not Requested'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    contact_person = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    sms_balance = models.IntegerField(default=0)
    sender_id = models.CharField(max_length=11, blank=True)
    sender_id_status = models.CharField(
        max_length=20, choices=SENDER_STATUS, default='none'
    )
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_sender_id(self):
        if self.sender_id_status == 'approved' and self.sender_id:
            return self.sender_id
        return 'NOTIFI'

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'notifi_schools'
        ordering = ['-created_at']
