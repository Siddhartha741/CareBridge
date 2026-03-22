from .models import Notification

def send_notification(user, message, category='system', link=None):
    """
    Creates a notification for a specific user.
    """
    if user:
        Notification.objects.create(
            recipient=user,
            message=message,
            category=category,
            link=link
        )