import uuid
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Doctor

# ========================================================
# 1. SPECIAL FORM FOR DOCTORS (No Username Field!)
# ========================================================
class DoctorCreationForm(forms.ModelForm):
    # We only ask for these 4 fields. Simple and clean.
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=False)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Doctor
        fields = ('email', 'first_name', 'last_name', 'password')

    def save(self, commit=True):
        user = super().save(commit=False)
        # 1. Set the password
        user.set_password(self.cleaned_data["password"])
        
        # 2. Force Role to Doctor
        user.role = 'doctor'
        
        # 3. Give a temp username (Model will swap it for real ID automatically)
        user.username = f"temp_{uuid.uuid4().hex[:8]}"
        
        # 4. FIXED: Set default values for fields not in the form
        user.is_verified = True
        user.patient_id = None
        user.google_auth = False  # <--- THIS FIXES THE INTEGRITY ERROR
        
        if commit:
            user.save()
        return user

# ========================================================
# 2. THE NEW "DOCTORS" ADMIN SECTION
# ========================================================
class DoctorAdmin(admin.ModelAdmin):
    add_form = DoctorCreationForm
    
    # Columns to show in the list
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_verified')
    
    # Only show actual doctors in this list
    def get_queryset(self, request):
        return super().get_queryset(request).filter(role='doctor')
    
    # Use our special form for adding
    def get_form(self, request, obj=None, **kwargs):
        defaults = {}
        if obj is None:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)

# ========================================================
# 3. STANDARD USER ADMIN (For everyone else)
# ========================================================
class CustomUserAdmin(UserAdmin):
    ordering = ('-date_joined',)
    list_display = ('username', 'role', 'first_name', 'email')
    fieldsets = ((None, {'fields': ('username', 'password')}), 
                 ('Personal', {'fields': ('first_name', 'last_name', 'email', 'role')}))

# Register both
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Doctor, DoctorAdmin)