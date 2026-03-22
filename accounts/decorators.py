from django.http import HttpResponseForbidden
from django.shortcuts import redirect

# This decorator ensures only authorized roles can access a view
def role_required(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if request.user.is_authenticated:
                # Check if the user's role is in the allowed list
                if request.user.role in allowed_roles:
                    return view_func(request, *args, **kwargs)
                else:
                    # If unauthorized, return a 403 Forbidden error
                    return HttpResponseForbidden("You are not authorized to view this page.")
            else:
                return redirect('login')
        return wrapper_func
    return decorator

# Specific decorators for easier use
def admin_only(view_func):
    return role_required(allowed_roles=['admin'])(view_func)

def doctor_only(view_func):
    return role_required(allowed_roles=['doctor'])(view_func)

def patient_only(view_func):
    return role_required(allowed_roles=['patient'])(view_func)