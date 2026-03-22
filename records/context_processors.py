from django.utils import timezone
from records.models import DailyCheckIn

def vitalsync_notification(request):
    """
    Checks if a logged-in patient has completed their Daily VitalSync Check-in.
    If not, it triggers a global banner.
    """
    context = {'needs_daily_checkin': False}

    # 🐛 FIX: Check if the user's role is specifically 'patient'
    if request.user.is_authenticated and getattr(request.user, 'role', '') == 'patient':
        today = timezone.now().date()
        
        # Check if a completed check-in exists for today
        checkin_completed = DailyCheckIn.objects.filter(
            patient=request.user, 
            date=today, 
            is_completed=True
        ).exists()

        # If they haven't completed it, trigger the notification
        if not checkin_completed:
            context['needs_daily_checkin'] = True

    return context