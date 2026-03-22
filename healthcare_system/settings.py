"""
Django settings for healthcare_system project.
"""

from pathlib import Path
import os  # Added to help with certain path operations if needed

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-#1_5&pux9nto8e3v9mr1m+tv4w@8nj_v%4-u_35jc*i2fg#=@8'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Custom Apps
    'accounts',
    'appointments',
    'records',
    'dashboard',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'healthcare_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # FIX 1: Point to the templates folder you created
        'DIRS': [BASE_DIR / 'templates'], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # --- ADDED FOR NOTIFICATIONS ---
                'dashboard.context_processors.notifications',
            ],
        },
    },
]

WSGI_APPLICATION = 'healthcare_system.wsgi.application'


# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'healthcare_db',
        'USER': 'admin',        
        'PASSWORD': 'admin123', 
        'HOST': 'localhost',
        'PORT': '3306',
    }
}


# Password validation
# Enforcing: Min 6 chars, 1 Uppercase, 1 Number, 1 Special Char

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 6, # Rule: Minimum 6 characters
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    # Custom rule for Uppercase and Special Char using Regex
    {
        'NAME': 'accounts.validators.ComplexPasswordValidator', 
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# FIX 2: Add this so Django finds the "static" folder you created
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# FIX 3: Media files (For Profile Pictures & Lab Reports)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Custom User Model
AUTH_USER_MODEL = 'accounts.CustomUser'

# REAL EMAIL CONFIGURATION (Gmail)
EMAIL_BACKEND = 'healthcare_system.email_backend.CustomEmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Replace this with YOUR actual Gmail address
EMAIL_HOST_USER = 'siddartha.namilikonda@gmail.com' 

# Paste the code you just generated here (keep the quotes!)
EMAIL_HOST_PASSWORD = 'dcma ltah wafh flvy' 

DEFAULT_FROM_EMAIL = 'CareBridge <no-reply@carebridge.com>'

# --- LOGIN/LOGOUT REDIRECTS ---

# After login, go to the 'home' URL (which handles the dashboard redirection)
LOGIN_REDIRECT_URL = 'home'

# After logout, go back to the landing page
LOGOUT_REDIRECT_URL = 'home'
# ==========================================
# PROFESSIONAL SESSION SECURITY SETTINGS
# ==========================================

# 1. LOGOUT ON BROWSER CLOSE
# This ensures that when the user closes the browser window, 
# they are effectively logged out. The cookie is deleted by the browser.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# 2. INACTIVITY TIMEOUT (30 Minutes)
# If the user is inactive for 30 minutes, their session expires.
# This is standard for healthcare/banking apps.
SESSION_COOKIE_AGE = 1800  # 1800 seconds = 30 minutes

# 3. RESET TIMER ON ACTIVITY
# If the user clicks a link, the 30-minute timer resets.
# If this is False, they would be kicked out after 30 mins even if working.
SESSION_SAVE_EVERY_REQUEST = True

# 4. SECURE COOKIES (For Production)
# Ensure cookies are only sent over secure connections (if using HTTPS)
# Set to False for local testing (HTTP), True for live deployment (HTTPS)
SESSION_COOKIE_SECURE = False  
CSRF_COOKIE_SECURE = False

# 5. REDIRECTS
# Where to go after logging in or out
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'  # Redirects to Landing Page after logout
# ==========================================
# PROFESSIONAL SECURITY & AUTO-LOGOUT SETTINGS
# ==========================================

# 1. IDLE TIMEOUT DURATION
# 600 seconds = 10 Minutes. 
# (Standard security practice for Hospital/Banking apps)
SESSION_COOKIE_AGE = 600 

# 2. RESET TIMER ON ACTIVITY
# True = Every time the user clicks a link or saves a form, the 10-minute timer restarts.
# False = The user gets kicked out exactly 10 mins after login, even if they are working.
# (We want True for a smooth professional experience)
SESSION_SAVE_EVERY_REQUEST = True 

# 3. CLOSE BROWSER = INSTANT LOGOUT
# True = If a doctor closes the tab or window, they are logged out immediately.
# This is crucial for shared hospital computers.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# 4. SECURITY HARDENING
# Ensures no one can access the session via JavaScript (prevents XSS attacks)
SESSION_COOKIE_HTTPONLY = True 

# ==========================================
# LOGIN/LOGOUT REDIRECTS
# ==========================================
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'
