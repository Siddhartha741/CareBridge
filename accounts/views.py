from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.core.mail import send_mail
from django.conf import settings
import random

from .forms import (
    PatientRegistrationForm, 
    PatientLoginForm, 
    StaffLoginForm, 
    UserProfileForm
)
from .models import Notification

User = get_user_model()

# ==========================================
# 1. PUBLIC PAGES
# ==========================================
def home_view(request):
    return render(request, 'home.html')

def services_view(request):
    return render(request, 'services.html')

# ==========================================
# 2. PATIENT LOGIN
# ==========================================
@never_cache
def patient_login_view(request):
    if request.user.is_authenticated:
        return redirect('patient_dashboard')

    if request.method == 'POST':
        form = PatientLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            # Security: Check if email is verified
            if not user.is_active:
                messages.error(request, "Account not activated. Please verify your email first.")
                return redirect('patient_login')
                
            login(request, user)
            
            if 'next' in request.GET:
                return redirect(request.GET.get('next'))
            return redirect('patient_dashboard')
        else:
            messages.error(request, "Invalid Credentials")
    else:
        form = PatientLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

# ==========================================
# 3. STAFF LOGIN
# ==========================================
@never_cache
def staff_login_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'doctor':
            return redirect('doctor_dashboard')
        elif request.user.role == 'admin':
            return redirect('/admin/')

    if request.method == 'POST':
        form = StaffLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            if user.role == 'doctor':
                return redirect('doctor_dashboard')
            elif user.role == 'admin':
                return redirect('/admin/')
            else:
                return redirect('home')
        else:
            messages.error(request, "Invalid Staff ID or Password")
    else:
        form = StaffLoginForm()
    
    return render(request, 'accounts/staff_login.html', {'form': form})

# ==========================================
# 4. REGISTRATION (SECURE FLOW)
# ==========================================
@never_cache
def register_view(request):
    if request.user.is_authenticated:
        return redirect('patient_dashboard')

    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST, request.FILES)
        
        if form.is_valid():
            # 1. Create user (Inactive)
            user = form.save(commit=False)
            user.is_active = False 
            user.save() 
            
            # 2. Generate OTP
            otp = str(random.randint(100000, 999999))
            
            # 3. Store in Session
            request.session['reg_otp'] = otp
            request.session['reg_user_id'] = user.id
            request.session['reg_email'] = user.email
            
            # 4. Send Email
            try:
                send_mail(
                    subject='CareBridge - Verify Your Account',
                    message=f'Welcome {user.first_name}!\n\nYour verification code is: {otp}\n\nEnter this code to activate your account.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False
                )
                print(f"--- OTP SENT TO {user.email}: {otp} ---")
                messages.success(request, f"Verification code sent to {user.email}")
                return redirect('verify_otp') 
                
            except Exception as e:
                user.delete()
                print(f"Email Error: {e}")
                messages.error(request, "Error sending email. Please try registering again.")
        else:
            messages.error(request, "Registration Failed. Please check inputs.")
    else:
        form = PatientRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

# ==========================================
# 5. OTP VERIFICATION
# ==========================================
@never_cache
def verify_otp_view(request):
    if 'reg_user_id' not in request.session:
        messages.error(request, "Session expired. Please register again.")
        return redirect('register')

    email = request.session.get('reg_email')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('reg_otp')
        user_id = request.session.get('reg_user_id')

        if entered_otp == session_otp:
            try:
                # 1. Activate User
                user = User.objects.get(id=user_id)
                user.is_active = True
                user.save()
                
                # 2. Create Welcome Notification
                create_notification(user, "Welcome to CareBridge", "Your account is verified. You can now book appointments.", "alert")
                
                # 3. Cleanup Session
                del request.session['reg_otp']
                del request.session['reg_user_id']
                del request.session['reg_email']
                
                messages.success(request, "Account verified! You can now login.")
                return redirect('patient_login')
                
            except User.DoesNotExist:
                messages.error(request, "User not found. Register again.")
                return redirect('register')
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, 'accounts/verify_otp.html', {'email': email})

# ==========================================
# 6. NOTIFICATIONS SYSTEM (UPDATED)
# ==========================================
@login_required
def notifications_view(request):
    """Display all notifications for the user"""
    notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
    unread_count = notifications.filter(is_read=False).count()
    
    return render(request, 'notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count
    })

@login_required
def mark_notification_read(request, notif_id):
    """Mark a single notification as read"""
    notification = get_object_or_404(Notification, id=notif_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications_page')

@login_required
def mark_all_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect('notifications_page')

@login_required
def delete_notification(request, notif_id):
    """Delete a single notification"""
    notification = get_object_or_404(Notification, id=notif_id, user=request.user)
    notification.delete()
    messages.success(request, "Notification removed.")
    return redirect('notifications_page')

@login_required
def clear_all_notifications(request):
    """Delete ALL notifications for the user"""
    Notification.objects.filter(user=request.user).delete()
    messages.success(request, "All notifications cleared.")
    return redirect('notifications_page')

def create_notification(user, title, message, category='alert'):
    """Helper function to create notifications from other views"""
    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        category=category
    )

# ==========================================
# 7. LOGOUT & PROFILE
# ==========================================
def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            
            # Security Notification for profile change
            create_notification(request.user, "Profile Updated", "Your profile details were recently updated.", "profile")

            if request.user.role == 'patient':
                return redirect('patient_dashboard')
            elif request.user.role == 'doctor':
                return redirect('doctor_dashboard')
            else:
                return redirect('home')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})

# ==========================================
# 8. STAFF PASSWORD RESET
# ==========================================
def staff_password_reset(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        if not username:
            messages.error(request, "Please enter your Staff ID.")
            return render(request, 'accounts/staff_password_reset.html')
        
        try:
            user = User.objects.get(username=username)
            if user.role not in ['doctor', 'admin']:
                messages.error(request, "This ID is not authorized.")
                return render(request, 'accounts/staff_password_reset.html')
            
            otp = str(random.randint(100000, 999999))
            request.session['reset_otp'] = otp
            request.session['reset_user_id'] = user.id
            
            send_mail(
                'Staff Password Reset',
                f'Your code is: {otp}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True
            )
            print(f"--- STAFF RESET OTP: {otp} ---")
            messages.success(request, f"Code sent to email linked to {username}")
            return redirect('staff_password_reset_verify')
            
        except User.DoesNotExist:
            messages.error(request, "Staff ID not found.")
            
    return render(request, 'accounts/staff_password_reset.html')

def staff_password_reset_verify(request):
    if 'reset_otp' not in request.session:
        return redirect('staff_password_reset')
    
    if request.method == 'POST':
        entered = request.POST.get('otp')
        actual = request.session.get('reset_otp')
        
        if entered == actual:
            request.session['reset_verified'] = True
            return redirect('staff_password_reset_confirm')
        else:
            messages.error(request, "Invalid Code.")
            
    return render(request, 'accounts/staff_password_reset_verify.html')

def staff_password_reset_confirm(request):
    if not request.session.get('reset_verified'):
        messages.error(request, "Unauthorized access. Verify OTP first.")
        return redirect('staff_password_reset')

    if request.method == 'POST':
        p1 = request.POST.get('new_password')
        p2 = request.POST.get('confirm_password')
        uid = request.session.get('reset_user_id')

        if not p1 or not p2:
            messages.error(request, "Password fields cannot be empty.")
            return render(request, 'accounts/staff_password_reset_confirm.html')

        if p1 == p2:
            try:
                user = User.objects.get(id=uid)
                user.set_password(p1)
                user.save()
                
                del request.session['reset_otp']
                del request.session['reset_user_id']
                del request.session['reset_verified']
                
                # Security notification
                create_notification(user, "Password Changed", "Your staff account password was successfully reset.", "profile")

                messages.success(request, "Password reset successful! Please login.")
                return redirect('staff_login')
                
            except User.DoesNotExist:
                messages.error(request, "User account not found.")
                return redirect('staff_password_reset')
        else:
            messages.error(request, "Passwords do not match.")

    return render(request, 'accounts/staff_password_reset_confirm.html')

# ==========================================
# 9. GENERAL HELPERS
# ==========================================
def resend_otp_view(request):
    if 'reg_otp' in request.session and 'reg_email' in request.session:
        otp = request.session['reg_otp']
        email = request.session['reg_email']
        send_mail(
            'Resend: Verification Code',
            f'Your code is: {otp}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=True
        )
        messages.success(request, "OTP resent successfully.")
    return redirect('verify_otp')