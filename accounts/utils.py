# accounts/utils.py
from .models import Notification

def send_notification(user, title, message, category='alert'):
    """
    Global helper to create notifications.
    Call this function from ANY view (Accounts or Appointments).
    """
    try:
        Notification.objects.create(
            user=user,
            title=title,
            message=message,
            category=category
        )
    except Exception as e:
        print(f"Error creating notification: {e}")