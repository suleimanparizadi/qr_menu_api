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

        # Total views all time
        total_view = menu.views.count()


        now = timezone.now()
        start_data = now - timedelta(days=days)


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


        peak_day = None
        if views_per_day:
            peak_day = max(views_per_day, key=lambda x: x['count']) # For each item x in the list, look at x['count']
                        # views_per_day is a list of dictionaries, not numbers

            return ServiceResult.success(
                data={
                    'total_view':total_view,
                    'today_view':todays_view,
                    'views_per_day':views_per_day,
                    'peak_day':peak_day,
                    'days_analytics': days
                },
            message="Analytics retrieved"
            )
        
