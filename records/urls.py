from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_report_view, name='upload_report'),
    path('my-reports/', views.patient_reports_view, name='patient_reports'),
]