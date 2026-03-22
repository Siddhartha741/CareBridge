from .models import Notification

def notifications(request):
    if request.user.is_authenticated:
        all_notifs = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:10] # Last 10
        unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return {
            'navbar_notifications': all_notifs,
            'unread_notification_count': unread_count
        }
    return {'navbar_notifications': [], 'unread_notification_count': 0}