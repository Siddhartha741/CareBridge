import uuid
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

# ==========================================
# 1. DEPARTMENT MODEL
# ==========================================
class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

# ==========================================
# 2. DOCTOR PROFILE MODEL
# ==========================================
class Doctor(models.Model):
    # Link to the Account (Login) - Restricts selection to only 'Doctor' roles
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='doctor_profile',
        limit_choices_to={'role': 'doctor'}
    )
    
    # Professional Details
    # blank=True allows this to be empty when auto-created via Signal
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Defaults prevent crashes during auto-creation
    specialization = models.CharField(max_length=100, default="General Physician", help_text="e.g. Heart Surgeon, Pediatrician")
    qualification = models.CharField(max_length=100, help_text="e.g. MBBS, MD", default="MBBS")
    experience_years = models.PositiveIntegerField(default=0)
    
    # Financials
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    
    # Availability & Schedule
    is_available = models.BooleanField(default=True)
    available_days = models.CharField(max_length=100, default="Mon-Fri", help_text="e.g. Mon-Fri")
    available_time = models.CharField(max_length=100, default="09:00 AM - 05:00 PM", help_text="e.g. 09:00 AM - 05:00 PM")

    def __str__(self):
        dept_name = self.department.name if self.department else "General"
        return f"Dr. {self.user.first_name} {self.user.last_name} ({dept_name})"

# ==========================================
# 3. APPOINTMENT MODEL
# ==========================================
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    # Links
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='patient_appointments',
        limit_choices_to={'role': 'patient'}
    )
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='doctor_appointments')
    
    # Schedule Details
    date = models.DateField()
    time = models.TimeField()
    reason = models.TextField()
    
    # Status Flow
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True) 
    
    # Video Call Link
    meeting_link = models.URLField(max_length=500, blank=True, null=True, help_text="Auto-generated video link")

    class Meta:
        ordering = ['-date', '-time']
        unique_together = ('doctor', 'date', 'time') # Prevent double booking

    def __str__(self):
        return f"Appt: {self.patient.username} with {self.doctor} on {self.date}"

# ==========================================
# 4. SIGNALS (AUTOMATIONS)
# ==========================================

# A. Auto-generate Meeting Link for Appointments
@receiver(post_save, sender=Appointment)
def generate_meeting_link(sender, instance, created, **kwargs):
    """
    Automatically creates a unique video meeting link when an appointment is booked.
    """
    if created and not instance.meeting_link:
        unique_room_id = f"CareBridge-{instance.id}-{uuid.uuid4().hex[:8]}"
        instance.meeting_link = f"https://meet.jit.si/{unique_room_id}"
        instance.save()

# B. Auto-create Doctor Profile (The Fix)
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_doctor_profile_signal(sender, instance, created, **kwargs):
    """
    Automatically creates a blank Doctor Profile whenever a User with role='doctor' is created.
    """
    if created and instance.role == 'doctor':
        # get_or_create prevents crashing if the profile already exists
        Doctor.objects.get_or_create(user=instance)