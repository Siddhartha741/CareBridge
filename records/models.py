from django.db import models
from django.conf import settings
from appointments.models import Appointment, Doctor

class MedicalReport(models.Model):
    # 1. Links (All set to NULL=True to bypass migration errors)
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='medical_report', null=True, blank=True)
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='medical_reports', null=True, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='authored_reports', null=True, blank=True)
    
    # 2. Clinical Data (With DEFAULTS to bypass errors)
    diagnosis = models.CharField(max_length=255, default="Pending Diagnosis", help_text="Main condition")
    symptoms = models.TextField(default="No symptoms recorded", help_text="Patient symptoms")
    medications = models.TextField(default="No medications prescribed", help_text="Prescribed medicines")
    
    # 3. Optional Fields
    lab_tests = models.TextField(blank=True, null=True, help_text="Required tests (optional)")
    doctor_notes = models.TextField(blank=True, null=True, help_text="Additional advice")
    
    # 4. File Attachment
    attachment = models.FileField(upload_to='reports/', blank=True, null=True, help_text="Upload Lab PDF or X-Ray")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        # Safety check in case patient is None during migration
        p_name = self.patient.username if self.patient else "Unknown Patient"
        return f"Report: {p_name} - {self.diagnosis}"