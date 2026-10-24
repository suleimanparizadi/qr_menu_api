import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

celery_app = Celery("qr_menu_api")

celery_app.config_from_object(
    "django.conf:settings",
    namespace="CELERY",
)

celery_app.autodiscover_tasks()



celery_app.conf.beat_schedule = {
    'cleanup-orphaned-qr-codes': {
        'task': 'apps.menu.tasks.cleanup_orphaned_qr_codes',
        'schedule': crontab(hour=3, minute=0, day_of_month='*/3'),
    },
    'cleanup-expired-otps': {
        'task': 'apps.accounts.tasks.cleanup_expired_otps',
        'schedule': crontab(hour=3, minute=0, day_of_month='*/3'),
    },
}