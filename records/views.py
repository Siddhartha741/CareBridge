from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.decorators import doctor_only, patient_only
from .forms import MedicalReportForm
from appointments.models import Doctor
from .models import MedicalReport

# ==========================================
#               DOCTOR VIEWS
# ==========================================

@login_required
@doctor_only
def upload_report_view(request):
    if request.method == 'POST':
        form = MedicalReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            
            # Auto-assign the uploading doctor
            try:
                report.doctor = request.user.doctor_profile
            except:
                report.doctor = Doctor.objects.get(user=request.user)
                
            report.save()
            messages.success(request, "Medical report uploaded successfully!")
            return redirect('doctor_dashboard')
    else:
        form = MedicalReportForm()

    return render(request, 'records/upload_report.html', {'form': form})


# ==========================================
#               PATIENT VIEWS
# ==========================================

@login_required
@patient_only
def patient_reports_view(request):
    # Fetch all reports for the logged-in user
    reports = MedicalReport.objects.filter(patient=request.user).order_by('-created_at')
    return render(request, 'records/patient_reports.html', {'reports': reports})