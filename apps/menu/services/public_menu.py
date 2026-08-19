from apps.menu.models import menu_model
from utils.service_result import ServiceResult
from django.utils import timezone




class PublicMenuService:

    def __init__(self, user):

        self.user = user



    def get_menu(self, menu_id):

        try:
            menu = menu_model.QRMenu.objects.get(id=menu_id, available=True)

        except menu_model.QRMenu.DoesNotExist:
            return ServiceResult.fail(
                message="Unable to find the menu"
            )


        # record the view
        menu_model.MenuView.objects.create(menu=menu)

        current_time = timezone.localtime().now()