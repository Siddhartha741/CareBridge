from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.template import loader
from django.core.mail import EmailMultiAlternatives

User = get_user_model()

# ==========================================
# 1. PATIENT REGISTRATION FORM (FIXED)
# ==========================================
# Changed parent to forms.ModelForm to avoid UserCreationForm conflicts
class PatientRegistrationForm(forms.ModelForm):
    # 1. Explicitly define password fields
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Password', 
            'id': 'id_password' # Critical for the 'eye' toggle script
        })
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Confirm Password', 
            'id': 'id_confirm_password'
        })
    )

    class Meta:
        model = User
        # 2. Define exactly which fields to save to the DB
        fields = [
            'first_name', 
            'last_name', 
            'username', 
            'email', 
            'phone_number', 
            'address', 
            'profile_picture'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Address'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

    # 3. Validation: Ensure passwords match
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        
        # Check if username/email already exists (extra safety)
        username = cleaned_data.get("username")
        email = cleaned_data.get("email")
        
        if username and User.objects.filter(username=username).exists():
            self.add_error('username', "This username is already taken.")
            
        if email and User.objects.filter(email=email).exists():
            self.add_error('email', "This email is already registered.")

        return cleaned_data

    # 4. Save: Hash password and set Role
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"]) # Hash password
        user.role = 'patient' # Force role
        if commit:
            user.save()
        return user

# ==========================================
# 2. LOGIN FORMS
# ==========================================
class PatientLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Password'
    }))

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if user.role != 'patient':
            raise forms.ValidationError("Access denied. This portal is for Patients only.")

class StaffLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Staff ID / Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Password'
    }))

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if user.role not in ['doctor', 'admin']:
            raise forms.ValidationError("Access denied. Restricted to Hospital Staff.")

# ==========================================
# 3. USER PROFILE FORM
# ==========================================
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address', 'readonly': 'readonly'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full Address'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

# ==========================================
# 4. STAFF PASSWORD RESET FORM
# ==========================================
class StaffPasswordResetForm(forms.Form):
    username = forms.CharField(
        max_length=150, 
        label="Staff ID / Username",
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter your Staff ID'
        })
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        try:
            user = User.objects.get(username__iexact=username, is_active=True)
        except User.DoesNotExist:
            raise forms.ValidationError("Access Denied: Staff ID not found.")

        is_authorized = (
            getattr(user, 'role', '') == 'doctor' or 
            user.is_staff or 
            user.is_superuser
        )

        if not is_authorized:
            raise forms.ValidationError("Access Denied: This account is not authorized for the Staff Portal.")
            
        if not user.email:
            raise forms.ValidationError("Error: No email address is linked to this Staff ID. Contact Admin.")

        self.user_cache = user
        return username

    def save(self, domain_override=None, subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html', use_https=False,
             token_generator=default_token_generator, from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None):
        user = self.user_cache
        email = user.email

        context = {
            'email': email,
            'domain': domain_override,
            'site_name': domain_override,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'user': user,
            'token': token_generator.make_token(user),
            'protocol': 'https' if use_https else 'http',
            **(extra_email_context or {}),
        }

        subject = loader.render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [email])
        
        if html_email_template_name:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, "text/html")

        email_message.send()
        return email