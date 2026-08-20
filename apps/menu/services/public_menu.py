from apps.menu.models import menu_model
from utils.service_result import ServiceResult
from django.utils import timezone
from django.db.models import Q



class PublicMenuService:



    def get_menu(self, menu_id):

        try:
            menu = menu_model.QRMenu.objects.get(id=menu_id, available=True)

        except menu_model.QRMenu.DoesNotExist:
            return ServiceResult.fail(
                message="Unable to find the menu"
            )


        # record the view
        menu_model.MenuView.objects.create(menu=menu)

        current_time = timezone.localtime().time()        
        sections = menu.sections.filter(
            Q(start_time__isnull=True , end_time__isnull=True) |
            Q(start_time__lte=current_time, end_time__gte=current_time)
        ).order_by('order').prefetch_related('items')


        if not sections.exists():
            return ServiceResult.fail(
                message="Menu currently unavailable",
                code="NO_ACTIVE_SECTIONS"
            )
        
        return ServiceResult.success(
            data={'menu':menu, 'sections':sections},
            message="Menu retrieved"
        )