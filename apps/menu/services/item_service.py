from apps.menu.models import menu_model
from utils.service_result import ServiceResult




class ItemService:

    def __init__(self, user):
        self.user = user


    def add_item(self, section_id, item, description, price, order=0):

        try:
            section = menu_model.MenuSection.objects.get(id=section_id, menu__user=self.user)    

        except menu_model.MenuSection.DoesNotExist:
            return ServiceResult.fail(
                message="unable to locate the section"
            )


        menu_item = menu_model.MenuItem.objects.create(
            section=section,
            item=item,
            description=description,
            price=price,
            order=order
        )


        return ServiceResult.success(
            data=menu_item,
            message="Item added"
        )



    def delete_item(self, item_id):

        ...