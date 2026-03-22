from django import forms
from accounts.models import CustomUser
import uuid

class UserProfileForm(forms.ModelForm):
    # --- READ-ONLY IDENTITY FIELDS ---
    patient_id = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control bg-light fw-bold text-dark', 'readonly': 'readonly'})
    )
    first_name = forms.CharField(
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Legal First Name'})
    )
    last_name = forms.CharField(
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Legal Last Name'})
    )
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={'class': 'form-control bg-light text-dark', 'readonly': 'readonly'})
    )
    
    # --- EDITABLE CONTACT DETAILS ---
    phone_number = forms.CharField(
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'})
    )
    address = forms.CharField(
        required=True, 
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Home Address'})
    )
    
    # Files
    profile_picture = forms.ImageField(
        required=False, 
        widget=forms.FileInput(attrs={'class': 'd-none'})
    )

    # --- SECURITY ---
    username = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'})
    )
    new_password = forms.CharField(
        required=False, 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'})
    )
    confirm_password = forms.CharField(
        required=False, 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'})
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'profile_picture', 'username']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.instance
        
        # 1. Generate/Show Patient ID
        if not user.patient_id:
            # If missing (old user), generate it now
            user.patient_id = f"P-{uuid.uuid4().hex[:6].upper()}"
            user.save()
        
        self.fields['patient_id'].initial = user.patient_id
        
        # 2. LOCK NAMES PERMANENTLY (Visual Lock)
        if user.first_name and user.last_name:
            self.fields['first_name'].widget.attrs.update({'readonly': 'readonly', 'class': 'form-control bg-light text-dark fw-bold'})
            self.fields['last_name'].widget.attrs.update({'readonly': 'readonly', 'class': 'form-control bg-light text-dark fw-bold'})
        
        # 3. LOCK EMAIL
        if user.email:
            self.fields['email'].widget.attrs.update({'readonly': 'readonly', 'class': 'form-control bg-light text-dark'})

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("new_password")
        confirm = cleaned_data.get("confirm_password")
        if password and confirm and password != confirm:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        
        if self.cleaned_data.get('username'):
            user.username = self.cleaned_data['username']
        if self.cleaned_data.get('new_password'):
            user.set_password(self.cleaned_data['new_password'])

        if commit:
            user.save()
            # Mark verified automatically if names are present
            if user.first_name and user.last_name and not user.is_verified:
                user.is_verified = True
                user.save()
        return user