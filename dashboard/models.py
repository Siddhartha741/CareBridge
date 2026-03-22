from django.db import models
from django.conf import settings
from django.utils.timesince import timesince

# --- 1. NOTIFICATION MODEL (For User Alerts) ---
class Notification(models.Model):
    TYPES = [
        ('appointment', 'Appointment'),
        ('report', 'Medical Report'),
        ('profile', 'Profile Update'),
        ('system', 'System Alert'),
    ]

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=TYPES, default='system')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=255, blank=True, null=True)  # URL to redirect to when clicked

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient}: {self.message}"
    
    @property
    def timesince(self):
        return timesince(self.created_at)


# --- 2. AUDIT LOG MODEL (For Security/History) ---
class AuditLog(models.Model):
    ACTION_TYPES = [
        ('LOGIN', 'User Login'),
        ('LOGOUT', 'User Logout'),
        ('CREATE', 'Created Record'),
        ('UPDATE', 'Updated Record'),
        ('DELETE', 'Deleted Record'),
        ('ACCESS', 'Access Denied/Granted'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    details = models.TextField(help_text="Details of what happened (e.g., 'Dr. Smith cancelled appointment #45')")
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # Good practice to store IP
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        username = self.user.username if self.user else "System/Unknown"
        return f"{username} - {self.action} at {self.timestamp}"