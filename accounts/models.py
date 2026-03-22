import uuid
import random
from django.db import models
from django.contrib.auth.models import AbstractUser

# ==========================================
# 1. CUSTOM USER MODEL
# ==========================================
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')
    
    # Patient ID: Unique for patients, Null for doctors
    patient_id = models.CharField(max_length=10, unique=True, null=True, blank=True)
    
    is_verified = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # 1. Logic: If NOT a patient, force patient_id to be None
        if self.role != 'patient':
            self.patient_id = None
        
        # 2. Logic: Generate Patient ID (P-XXXXXX)
        elif self.role == 'patient' and not self.patient_id:
            while True:
                new_id = f"P-{uuid.uuid4().hex[:6].upper()}"
                if not CustomUser.objects.filter(patient_id=new_id).exists():
                    self.patient_id = new_id
                    break

        # 3. Logic: Generate Doctor ID (d123456cb)
        if self.role == 'doctor':
            self.is_verified = True  # Doctors created by admin are verified by default
            # Only generate if username is missing or starts with temp_
            if not self.username or self.username.startswith('temp_'):
                unique_found = False
                while not unique_found:
                    random_digits = random.randint(100000, 999999)
                    new_username = f"d{random_digits}cb"
                    if not CustomUser.objects.filter(username=new_username).exists():
                        self.username = new_username
                        unique_found = True
            
        super().save(*args, **kwargs)

# ==========================================
# 2. DOCTOR PROXY MODEL
# ==========================================
class Doctor(CustomUser):
    class Meta:
        proxy = True
        verbose_name = 'Doctor'
        verbose_name_plural = 'Doctors'

# ==========================================
# 3. NOTIFICATION MODEL
# ==========================================
class Notification(models.Model):
    CATEGORY_CHOICES = [
        ('appointment', 'Appointment'),
        ('alert', 'System Alert'),
        ('report', 'Medical Report'),
        ('profile', 'Profile Update'), # Added this for Profile Edit notifications
    ]

    # 'related_name' prevents conflicts with other apps
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='account_notifications')
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='alert')
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"