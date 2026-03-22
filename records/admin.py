from django.contrib import admin
from .models import MedicalReport

@admin.register(MedicalReport)
class MedicalReportAdmin(admin.ModelAdmin):
    # Updated to match your new Model fields
    list_display = ('patient', 'doctor', 'diagnosis', 'created_at')
    
    # Search by patient name, doctor name, or diagnosis
    search_fields = ('patient__username', 'doctor__user__username', 'diagnosis')
    
    # Filter by date or doctor
    list_filter = ('created_at', 'doctor')