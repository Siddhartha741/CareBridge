from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required 
from .models import Appointment, Doctor
from accounts.models import CustomUser, Notification
from datetime import datetime
from django.utils import timezone

# ==========================================
# HELPER: SEND NOTIFICATION
# ==========================================
def send_notification(user, message, category='alert', link=None):
    """
    Creates a persistent notification in the database.
    """
    try:
        Notification.objects.create(
            user=user,
            title="Notification", 
            message=message,
            category=category,
            # link=link # Uncomment if your Notification model has a link field
        )
    except Exception as e:
        print(f"Error sending notification: {e}")

# ==========================================
#               PATIENT VIEWS
# ==========================================

@login_required
@role_required(allowed_roles=['patient'])
def book_appointment_view(request):
    # --- AUTO-SYNC: Ensure Doctor Profiles Exist ---
    # This prevents the empty dropdown issue if doctors are added via Admin
    doctor_users = CustomUser.objects.filter(role='doctor')
    for doc_user in doctor_users:
        if not Doctor.objects.filter(user=doc_user).exists():
            Doctor.objects.create(user=doc_user)
            print(f"Auto-created profile for {doc_user.username}")
    # -----------------------------------------------

    # Fetch Doctor Profiles for dropdown
    doctors = Doctor.objects.all().select_related('user')

    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        date = request.POST.get('date')
        time = request.POST.get('time')
        reason = request.POST.get('reason')

        # 1. Validation
        if not all([doctor_id, date, time]):
            messages.error(request, "Please select a doctor, date, and time.")
            return redirect('book_appointment')

        # 2. Clinic Hours Validation (9 AM - 5 PM)
        try:
            appt_time = datetime.strptime(time, "%H:%M").time()
            start_time = datetime.strptime("09:00", "%H:%M").time()
            end_time = datetime.strptime("17:00", "%H:%M").time()

            if not (start_time <= appt_time <= end_time):
                messages.error(request, "❌ Clinic hours are 9:00 AM to 5:00 PM.")
                return redirect('book_appointment')
        except ValueError:
            messages.error(request, "Invalid time format.")
            return redirect('book_appointment')

        # 3. Get Doctor Instance
        target_doctor = get_object_or_404(Doctor, id=doctor_id)

        # 4. Check Availability (Double Booking)
        if Appointment.objects.filter(
            doctor=target_doctor, 
            date=date, 
            time=time, 
            status__in=['pending', 'confirmed', 'approved']
        ).exists():
            messages.error(request, "⚠️ Doctor is unavailable at this time. Please select another slot.")
            return redirect('book_appointment')

        # 5. Create Appointment
        Appointment.objects.create(
            patient=request.user,
            doctor=target_doctor,
            date=date,
            time=time,
            reason=reason,
            status='pending' 
        )

        # --- NOTIFICATIONS ---
        # To Doctor
        send_notification(
            user=target_doctor.user, 
            message=f"New Appointment Request: {request.user.first_name} requested {date} at {time}.",
            category="appointment",
            link='/dashboard/doctor-dashboard/'
        )

        # To Patient
        send_notification(
            user=request.user,
            message=f"Request sent to Dr. {target_doctor.user.last_name}. Waiting for confirmation.",
            category="appointment",
            link='/dashboard/patient-dashboard/'
        )

        messages.success(request, "Appointment request sent successfully!")
        return redirect('patient_dashboard')

    return render(request, 'appointments/book_appointment.html', {'doctors': doctors})


@login_required
@role_required(allowed_roles=['patient'])
def cancel_appointment_view(request, pk):
    """
    Handles appointment cancellation by Patient.
    """
    appointment = get_object_or_404(Appointment, id=pk, patient=request.user)

    if appointment.status in ['approved', 'pending', 'confirmed', 'scheduled']:
        appointment.status = 'cancelled'
        appointment.save()
        
        # Notify Doctor
        send_notification(
            user=appointment.doctor.user,
            message=f"Patient {request.user.first_name} cancelled their appointment for {appointment.date}.",
            category="alert",
            link='/dashboard/doctor-dashboard/'
        )

        # Notify Patient
        send_notification(
            user=request.user,
            message=f"You cancelled your appointment with Dr. {appointment.doctor.user.last_name}.",
            category="alert"
        )
        
        messages.success(request, "Appointment cancelled successfully.")
    else:
        messages.error(request, "You cannot cancel this appointment.")
    
    return redirect('patient_dashboard')


@login_required
@role_required(allowed_roles=['patient'])
def appointment_history_view(request):
    appointments = Appointment.objects.filter(patient=request.user).order_by('-date', '-time')
    return render(request, 'appointments/appointment_history.html', {'appointments': appointments})


# ==========================================
#               DOCTOR VIEWS
# ==========================================

@login_required
@role_required(allowed_roles=['doctor'])
def approve_appointment_view(request, pk):
    """
    Doctor Confirms/Approves a request.
    """
    # Securely find appointment for logged-in doctor
    appointment = get_object_or_404(Appointment, id=pk, doctor__user=request.user)

    if appointment.status == 'pending':
        appointment.status = 'confirmed' # Standardizing on 'confirmed'
        appointment.save()

        send_notification(
            user=appointment.patient,
            message=f"Dr. {request.user.last_name} has confirmed your appointment for {appointment.date}.",
            category="appointment",
            link='/dashboard/patient-dashboard/'
        )

        messages.success(request, "Appointment Confirmed.")
    
    return redirect('doctor_dashboard')


@login_required
@role_required(allowed_roles=['doctor'])
def reject_appointment_view(request, pk):
    """
    Doctor Rejects a request.
    """
    appointment = get_object_or_404(Appointment, id=pk, doctor__user=request.user)

    if appointment.status == 'pending':
        appointment.status = 'rejected'
        appointment.save()

        send_notification(
            user=appointment.patient,
            message=f"Dr. {request.user.last_name} is unavailable for the requested slot. Please reschedule.",
            category="appointment",
            link='/appointments/book/'
        )
        messages.success(request, "Appointment Rejected.")

    return redirect('doctor_dashboard')


@login_required
@role_required(allowed_roles=['doctor'])
def complete_appointment_view(request, pk):
    """
    Marks appointment as completed.
    """
    appointment = get_object_or_404(Appointment, id=pk, doctor__user=request.user)

    if appointment.status in ['confirmed', 'approved', 'scheduled']:
        appointment.status = 'completed'
        appointment.completed_at = timezone.now()
        appointment.save()
        
        send_notification(
            user=appointment.patient,
            message=f"Your visit with Dr. {request.user.last_name} is marked as complete.",
            category="report"
        )
        
        messages.success(request, "Appointment marked as completed.")
        
        # Redirect to create report or stay on dashboard
        # return redirect('create_report', appointment_id=appointment.id) 
        return redirect('doctor_dashboard')
    
    return redirect('doctor_dashboard')