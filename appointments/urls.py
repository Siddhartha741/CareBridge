from django.urls import path
from . import views

urlpatterns = [
    path('book/', views.book_appointment_view, name='book_appointment'),
    path('cancel/<int:pk>/', views.cancel_appointment_view, name='cancel_appointment'),
    # New: Full History
    path('history/', views.appointment_history_view, name='appointment_history'),
    path('complete/<int:pk>/', views.complete_appointment_view, name='complete_appointment'),
]
