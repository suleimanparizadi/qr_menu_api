# apps/accounts/tasks.py
import logging
from celery import shared_task
from django.utils import timezone
from apps.accounts.models.otp_models import OTP

logger = logging.getLogger(__name__)


@shared_task
def cleanup_expired_otps():
    """
    Delete OTPs that have expired.
    Runs every 3 days during low-traffic hours.
    """
    now = timezone.now()
    
    # Count before deletion (for logging)
    total_before = OTP.objects.count()
    
    # Delete expired OTPs
    deleted_count, _ = OTP.objects.filter(expired_at__lt=now).delete()
    
    total_after = OTP.objects.count()
    
    logger.info(
        f"OTP cleanup: {deleted_count} deleted, "
        f"{total_after} remaining (was {total_before})"
    )
    
    return {
        "success": True,
        "deleted": deleted_count,
        "remaining": total_after,
    }