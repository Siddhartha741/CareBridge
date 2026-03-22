from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
import random
import json

# Custom Decorators & Utilities
from accounts.decorators import role_required
from .forms import UserProfileForm

# Import Models
from appointments.models import Appointment, Doctor
from accounts.models import CustomUser, Notification
from records.models import MedicalReport 

# ==========================================
# HELPER: SEND NOTIFICATION
# ==========================================
def send_notification(user, message, category='alert', link=None):
    """
    Creates a notification in the accounts.Notification table.
    """
    try:
        Notification.objects.create(
            user=user,
            title="Notification", 
            message=message,
            category=category,
            # link=link  # Uncomment if your model has a link field
        )
    except Exception as e:
        print(f"Error sending notification: {e}")

# ==========================================
# 1. PATIENT DASHBOARD (Home)
# ==========================================
@never_cache
@login_required
@role_required(allowed_roles=['patient'])
def patient_dashboard(request):
    # Fetch appointments for the logged-in patient with optimized queries
    my_appointments = Appointment.objects.filter(patient=request.user)\
                                         .select_related('doctor', 'doctor__user')\
                                         .order_by('-date', '-time')
    
    # Counts
    upcoming_count = my_appointments.filter(status__in=['pending', 'scheduled', 'confirmed']).count()
    completed_count = my_appointments.filter(status='completed').count()
    
    # Reports Count
    report_count = MedicalReport.objects.filter(patient=request.user).count()
    
    # Recent Activity (First 5)
    recent_activity = my_appointments[:5]

    # Notifications
    recent_notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-timestamp')[:3]

    context = {
        'upcoming_count': upcoming_count,
        'completed_count': completed_count,
        'report_count': report_count,
        'recent_activity': recent_activity,
        'recent_notifications': recent_notifications
    }
    return render(request, 'dashboard/patient_home.html', context)


# ==========================================
# 2. PATIENT: UPCOMING APPOINTMENTS
# ==========================================
@login_required
@role_required(allowed_roles=['patient'])
def patient_upcoming(request):
    """
    Shows pending and confirmed appointments.
    """
    appointments = Appointment.objects.filter(
        patient=request.user, 
        status__in=['pending', 'confirmed', 'scheduled']
    ).select_related('doctor', 'doctor__user').order_by('date', 'time')
    
    return render(request, 'dashboard/patient_upcoming.html', {'appointments': appointments})


# ==========================================
# 3. PATIENT: HISTORY (COMPLETED)
# ==========================================
@login_required
@role_required(allowed_roles=['patient'])
def patient_history(request):
    """
    Shows completed appointments with links to medical reports.
    """
    appointments = Appointment.objects.filter(
        patient=request.user, 
        status='completed'
    ).select_related('doctor', 'doctor__user').order_by('-date', '-time')
    
    return render(request, 'dashboard/patient_history.html', {'appointments': appointments})


# ==========================================
# 4. DOCTOR DASHBOARD (FIXED & AUTO-SYNC)
# ==========================================
@never_cache
@login_required
@role_required(allowed_roles=['doctor'])
def doctor_dashboard(request):
    # --- AUTO-SYNC: Ensure Doctor Profile Exists ---
    # This creates a profile automatically if it's missing (e.g., added via Admin)
    # This prevents the "Doctor matching query does not exist" crash.
    doctor_profile, created = Doctor.objects.get_or_create(user=request.user)
    
    if created:
        print(f"Auto-created Doctor Profile for {request.user.username}")
    # -----------------------------------------------

    today = timezone.now().date()

    # 1. PENDING REQUESTS (For the "Appointment Requests" section)
    # Use select_related to get patient details efficiently
    pending_appointments = Appointment.objects.filter(
        doctor=doctor_profile,
        status='pending'
    ).select_related('patient').order_by('date', 'time')

    # 2. TODAY'S SCHEDULE (Confirmed/Scheduled)
    todays_appointments = Appointment.objects.filter(
        doctor=doctor_profile, 
        date=today,
        status__in=['confirmed', 'scheduled', 'approved']
    ).select_related('patient').order_by('time')
    
    # 3. UPCOMING (Future dates, Confirmed)
    upcoming_appointments = Appointment.objects.filter(
        doctor=doctor_profile,
        date__gte=today,
        status__in=['confirmed', 'scheduled', 'approved']
    ).select_related('patient').order_by('date', 'time')
    
    # 4. STATS
    total_patients_count = Appointment.objects.filter(doctor=doctor_profile).values('patient').distinct().count()
    pending_count = pending_appointments.count()
    completed_today = Appointment.objects.filter(doctor=doctor_profile, date=today, status='completed').count()
    total_count = Appointment.objects.filter(doctor=doctor_profile).count()

    # 5. Notifications
    recent_notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')[:5]

    context = {
        'doctor': request.user, # Use user object for name
        'pending_appointments': pending_appointments, # CRITICAL: Pass requests to template
        'todays_appointments': todays_appointments,
        'appointments': upcoming_appointments, 
        'total_patients_count': total_patients_count,
        'pending_count': pending_count,
        'completed_today': completed_today,
        'today_count': todays_appointments.count(), 
        'total_count': total_count, 
        'notifications': recent_notifications
    }
    return render(request, 'dashboard/doctor_home.html', context)


# ==========================================
# 5. ADMIN DASHBOARD
# ==========================================
@never_cache
@login_required
@role_required(allowed_roles=['admin'])
def admin_dashboard(request):
    total_patients = CustomUser.objects.filter(role='patient').count()
    total_doctors = CustomUser.objects.filter(role='doctor').count()
    total_appointments = Appointment.objects.count()
    
    context = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_appointments': total_appointments,
    }
    return render(request, 'dashboard/admin_home.html', context)


# ==========================================
# 6. DOCTOR'S PATIENT DIRECTORY
# ==========================================
@login_required
@role_required(allowed_roles=['doctor'])
def doctor_patient_list(request):
    # Ensure profile exists
    doctor_profile, _ = Doctor.objects.get_or_create(user=request.user)

    patient_ids = Appointment.objects.filter(doctor=doctor_profile).values_list('patient_id', flat=True).distinct()
    patients = CustomUser.objects.filter(id__in=patient_ids)
    today = timezone.now().date()

    for patient in patients:
        upcoming_appt = Appointment.objects.filter(
            patient=patient, 
            doctor=doctor_profile, 
            date__gte=today
        ).order_by('date', 'time').first()

        if upcoming_appt:
            patient.display_appt = upcoming_appt
            if upcoming_appt.date == today:
                patient.appt_status = 'Today'
                patient.status_color = 'warning'
            else:
                patient.appt_status = 'Upcoming'
                patient.status_color = 'primary'
        else:
            last_appt = Appointment.objects.filter(
                patient=patient, 
                doctor=doctor_profile, 
                date__lt=today
            ).order_by('-date', '-time').first()
            
            patient.display_appt = last_appt
            patient.appt_status = 'Last Visit'
            patient.status_color = 'secondary'

    return render(request, 'dashboard/doctor_patients.html', {'patients': patients})


# ==========================================
# 7. COMPLETE APPOINTMENT (Doctor Action)
# ==========================================
@login_required
@role_required(allowed_roles=['doctor'])
def complete_appointment(request, appointment_id):
    # Securely get the appointment for this doctor
    doctor_profile = get_object_or_404(Doctor, user=request.user)
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor_profile)
    
    # Update Status
    appointment.status = 'completed'
    appointment.completed_at = timezone.now()
    appointment.save()
    
    # Notify Patient
    send_notification(
        user=appointment.patient,
        message=f"Your appointment with Dr. {request.user.last_name} is complete. Report pending.",
        category='report'
    )

    messages.success(request, "Appointment finished. Please write the medical report.")
    
    # Redirect to Create Report (Ensure 'create_report' URL exists in records/urls.py)
    # If not ready, redirect back to dashboard
    return redirect('create_report', appointment_id=appointment.id)


# ==========================================
# 8. JOIN MEETING (Auto-Complete Logic)
# ==========================================
@login_required
def join_meeting(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Security: Ensure current user is the assigned doctor
    if request.user.role == 'doctor' and appointment.doctor.user == request.user:
        if appointment.status != 'completed':
            appointment.status = 'completed'
            appointment.completed_at = timezone.now()
            appointment.save()
            messages.success(request, "Meeting started.")
            
            send_notification(
                user=appointment.patient,
                message=f"Dr. {request.user.last_name} has joined the call.",
                category='appointment'
            )
    
    if appointment.meeting_link:
        return redirect(appointment.meeting_link)
    else:
        messages.error(request, "Meeting link not available.")
        return redirect('doctor_dashboard')


# ==========================================
# 9. CONFIRM APPOINTMENT (Doctor Accepts Request)
# ==========================================
@login_required
@role_required(allowed_roles=['doctor'])
def confirm_appointment(request, appointment_id):
    # Ensure Doctor Profile
    doctor_profile = get_object_or_404(Doctor, user=request.user)
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor_profile)
    
    if appointment.status == 'pending':
        appointment.status = 'confirmed' # OR 'approved', match your model choices
        appointment.save()
        messages.success(request, "Appointment confirmed successfully.")
        
        # Notify Patient
        send_notification(
            user=appointment.patient,
            message=f"Dr. {request.user.last_name} confirmed your appointment for {appointment.date}.",
            category='appointment'
        )
    
    return redirect('doctor_dashboard')


# ==========================================
# 10. DOCTOR CANCEL APPOINTMENT
# ==========================================
@login_required
@role_required(allowed_roles=['doctor'])
def doctor_cancel_appointment(request, appointment_id):
    doctor_profile = get_object_or_404(Doctor, user=request.user)
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor_profile)
    
    appointment.status = 'cancelled'
    appointment.save()
    messages.warning(request, "Appointment has been cancelled.")
    
    # Notify Patient
    send_notification(
        user=appointment.patient,
        message=f"Dr. {request.user.last_name} has cancelled your appointment.",
        category='alert'
    )
    
    return redirect('doctor_dashboard')


# ==========================================
# 11. PATIENT CANCEL APPOINTMENT
# ==========================================
@login_required
@role_required(allowed_roles=['patient'])
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    
    if appointment.status != 'completed':
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, "Appointment cancelled successfully.")
        
        # Notify Doctor
        send_notification(
            user=appointment.doctor.user,
            message=f"Patient {request.user.first_name} cancelled their appointment.",
            category='alert'
        )
    else:
        messages.error(request, "Cannot cancel a completed appointment.")
        
    return redirect('patient_dashboard')


# ==========================================
# 12. REPORT ISSUE (Patient Flags Missed Appt)
# ==========================================
@login_required
@role_required(allowed_roles=['patient'])
def report_appointment_issue(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    
    appointment.status = 'doctor_missed'
    appointment.save()
    
    # Notify Support
    send_notification(
        user=request.user,
        message=f"Report received for appointment with Dr. {appointment.doctor.user.last_name}.",
        category='support'
    )
    
    messages.success(request, "Issue reported. Support will contact you.")
    return redirect('patient_dashboard')


# ==========================================
# 13. SEND STATUS (Late/Ready/Reschedule)
# ==========================================
@login_required
@require_POST
def send_appointment_status(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    status_type = request.POST.get('status_type')
    
    messages_map = {
        'late_5': f"Patient {request.user.first_name} is 5 mins late.",
        'late_10': f"Patient {request.user.first_name} is 10 mins late.",
        'ready': f"Patient {request.user.first_name} is ready.",
        'cant_make': f"Patient {request.user.first_name} cannot make it."
    }
    
    msg = messages_map.get(status_type)
    
    if msg:
        send_notification(
            user=appointment.doctor.user,
            message=msg,
            category='appointment'
        )
        messages.success(request, "Status update sent to doctor.")
    
    return redirect('patient_dashboard')


# ==========================================
# 14. VIEW ALL APPOINTMENTS
# ==========================================
@login_required
@role_required(allowed_roles=['patient'])
def appointment_list(request):
    appointments = Appointment.objects.filter(patient=request.user).order_by('-date', '-time')
    return render(request, 'dashboard/appointment_list.html', {'appointments': appointments})


# ==========================================
# 15. PROFILE SETTINGS
# ==========================================
@never_cache
@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            
            send_notification(
                user=request.user,
                message="Your profile details were updated.",
                category='profile'
            )
            
            if request.user.role == 'doctor':
                return redirect('doctor_dashboard')
            else:
                return redirect('patient_dashboard')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'dashboard/profile.html', {'form': form})


# ==========================================
# 16. NOTIFICATIONS PAGE
# ==========================================
@never_cache
@login_required
def notifications_page(request):
    # Fetch from accounts.models.Notification (using 'user' field)
    notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
    unread_count = notifications.filter(is_read=False).count()
    
    return render(request, 'dashboard/notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count
    })

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications_page')

@login_required
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('notifications_page')

@login_required
def clear_all_notifications(request):
    Notification.objects.filter(user=request.user).delete()
    messages.success(request, "All notifications cleared.")
    return redirect('notifications_page')

@login_required
def delete_notification(request, notif_id):
    notification = get_object_or_404(Notification, id=notif_id, user=request.user)
    notification.delete()
    messages.success(request, "Notification removed.")
    return redirect('notifications_page')


# ==========================================
# 17. AJAX: SECURITY OTP
# ==========================================
def send_security_otp(request):
    if request.method == "POST" and request.user.is_authenticated:
        otp = str(random.randint(100000, 999999))
        request.session['security_otp'] = otp
        request.session.set_expiry(300) 

        try:
            send_mail(
                "Security Code - CareBridge",
                f"Your OTP: {otp}",
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email]
            )
            return JsonResponse({'status': 'success', 'message': 'OTP sent.'})
        except:
            return JsonResponse({'status': 'error', 'message': 'Email failed.'})
    return JsonResponse({'status': 'error'})

def verify_security_otp(request):
    if request.method == "POST":
        data = json.loads(request.body)
        if data.get('otp') == request.session.get('security_otp'):
            del request.session['security_otp']
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'message': 'Invalid OTP.'})
    return JsonResponse({'status': 'error'})