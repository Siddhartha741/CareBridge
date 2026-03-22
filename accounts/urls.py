from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # ==========================================
    # 1. LANDING & SERVICES
    # ==========================================
    path('', views.home_view, name='home'),
    path('services/', views.services_view, name='services'),

    # ==========================================
    # 2. LOGIN PATHS
    # ==========================================
    # "Catch-all" login (points to patient login to prevent errors)
    path('login/', views.patient_login_view, name='login'),
    
    path('login/patient/', views.patient_login_view, name='patient_login'),
    path('login/staff/', views.staff_login_view, name='staff_login'),

    # ==========================================
    # 3. AUTH PATHS
    # ==========================================
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # ==========================================
    # 4. OTP PATHS (General)
    # ==========================================
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('resend-otp/', views.resend_otp_view, name='resend_otp'),

    # ==========================================
    # 5. PROFILE & NOTIFICATIONS (Updated)
    # ==========================================
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    
    # Notification Page
    path('notifications/', views.notifications_view, name='notifications_page'),
    
    # Notification Actions (New)
    path('notifications/read/<int:notif_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/read/all/', views.mark_all_read, name='mark_all_read'),
    path('notifications/delete/<int:notif_id>/', views.delete_notification, name='delete_notification'),
    path('notifications/delete/all/', views.clear_all_notifications, name='clear_all_notifications'),

    # ==========================================
    # 6. PATIENT PASSWORD RESET (Django Default)
    # ==========================================
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), 
         name='password_reset'),

    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), 
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), 
         name='password_reset_confirm'),

    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), 
         name='password_reset_complete'),

    # ==========================================
    # 7. STAFF PASSWORD RESET (Custom OTP Flow)
    # ==========================================
    # Step 1: Enter Staff ID
    path('login/staff/password-reset/', views.staff_password_reset, name='staff_password_reset'),
    
    # Step 2: Enter OTP Code
    path('login/staff/password-reset/verify/', views.staff_password_reset_verify, name='staff_password_reset_verify'),
    
    # Step 3: Set New Password
    path('login/staff/password-reset/confirm/', views.staff_password_reset_confirm, name='staff_password_reset_confirm'),
]