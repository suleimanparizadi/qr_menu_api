from apps.menu.models import menu_model
from utils.service_result import ServiceResult
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncDate
from datetime import timedelta



class MenuAnalyticsService:

    def __init__(self, user):
        self.user = user




    def get_analytics(self, menu_id, days=7):

        try:
            menu = menu_model.QRMenu.objects.get(id=menu_id, user=self.user)

        except menu_model.QRMenu.DoesNotExist:
            return ServiceResult.fail(
                message="Unable to find the menu",
                code="MENU_NOT_FOUND"
            )

        now = timezone.now()
        start_data = now - timedelta(days=days)

        # Total views all time
        total_view = menu.views.count()


        # Views today
        todays_view = menu.views.filter(
            viewed_at__data=now.date()
        ).count()


        # Views per day for the last N days
        views_per_day = (
            menu.view.filter(viewed_at__gte=start_data)
            .annotate(data=TruncDate('viewed_at')).values('data').annotate(
                count=Count('id')).order_by('data')
                )



