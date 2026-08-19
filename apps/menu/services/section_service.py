from apps.menu.models import menu_model
from utils.service_result import ServiceResult






class SectionService:


    def __init__(self, user):

        self.user = user


    def create_section(self, menu_id, name, start_time=None, end_time=None, order=0):

        try:
            menu = menu_model.QRMenu.objects.get(id=menu_id, user=self.user)

        except menu_model.QRMenu.DoesNotExist:
            return ServiceResult.fail(
                message="Unable to find the menu"
            )

        section = menu_model.MenuSection.objects.create(
            menu=menu,
            name=name,
            start_time=start_time,
            end_time=end_time,
            order=order
        )


        return ServiceResult.success(
            data={'section':section},
            message="Section created successfully"
        )



    def delete_section(self, section_id):

        try:
            section = menu_model.MenuSection.objects.get(
                id=section_id,
                menu__user=self.user
                )

        except menu_model.MenuSection.DoesNotExist:
            return ServiceResult.fail(
                message="unable to find section"
            )

        section.delete()

        return ServiceResult.success(
            message="Section deleted successfully"
        )

    