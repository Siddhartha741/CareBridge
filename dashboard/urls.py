from django.urls import path
from . import views

urlpatterns = [
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('doctor-dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('patient-dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor/my-patients/', views.doctor_patient_list, name='doctor_patient_list'),
    path('patient/appointments/', views.appointment_list, name='appointment_list'), # Fixed the error
    path('patient/cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('profile/settings/', views.profile, name='profile'),
    path('appointment/join/<int:appointment_id>/', views.join_meeting, name='join_meeting'),
    path('appointment/doctor-cancel/<int:appointment_id>/', views.doctor_cancel_appointment, name='doctor_cancel_appointment'),
   path('notifications/', views.notifications_page, name='notifications_page'), # <--- NEW PAGE
    path('notifications/read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/read-all/', views.mark_all_read, name='mark_all_read'),
    path('patient/upcoming/', views.patient_upcoming, name='patient_upcoming'),
    path('patient/history/', views.patient_history, name='patient_history'),
    path('notifications/clear-all/', views.clear_all_notifications, name='clear_all_notifications'),
    path('send-security-otp/', views.send_security_otp, name='send_security_otp'),
    path('verify-security-otp/', views.verify_security_otp, name='verify_security_otp'),
    # Add this inside urlpatterns
path('appointment/status-update/<int:appointment_id>/', views.send_appointment_status, name='send_appointment_status'),
]