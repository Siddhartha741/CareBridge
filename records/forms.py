from django import forms
from .models import MedicalReport

class MedicalReportForm(forms.ModelForm):
    class Meta:
        model = MedicalReport
        # These fields match the new model structure
        fields = ['diagnosis', 'symptoms', 'medications', 'lab_tests', 'doctor_notes', 'attachment']
        
        widgets = {
            'diagnosis': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., Viral Fever, Acute Bronchitis'
            }),
            'symptoms': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Patient complaints (e.g., High fever, cough...)'
            }),
            'medications': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Prescription details (e.g., Paracetamol 500mg BD...)'
            }),
            'lab_tests': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2, 
                'placeholder': 'Required tests (optional)'
            }),
            'doctor_notes': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2, 
                'placeholder': 'Dietary advice, rest recommendations, etc.'
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }

    # We removed the __init__ method for patient filtering because 
    # the patient is now automatically selected based on the appointment in the view.