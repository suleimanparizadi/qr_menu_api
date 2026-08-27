from apps.menu.models import menu_model
from utils.service_result import ServiceResult



class ItemService:

    def __init__(self, user):
        self.user = user


    def add_items(self, section_id, items_data):

        try:
            section = menu_model.MenuSection.objects.get(id=section_id, menu__user=self.user)    

        except menu_model.MenuSection.DoesNotExist:
            return ServiceResult.fail(
                message="unable to locate the section"
            )


        items_to_create = []

        for index, item_data in enumerate(items_data):

            item = menu_model.MenuItem(
                section=section,
                item=item_data['item'],
                description=item_data.get('description', ''),
                price=item_data['price'],
                order=item_data.get('order', index)
            )
            items_to_create.append(item)

        menu_model.MenuItem.objects.bulk_create(items_to_create)

        return ServiceResult.success(
            data={'items_count':len(items_to_create)},
                  message=f"{len(items_to_create)} items added successfully."
        )



    def delete_item(self, item_id):

        try:
            item = menu_model.MenuItem.objects.get(id=item_id, section__menu__user=self.user)    

        except menu_model.MenuItem.DoesNotExist:
            return ServiceResult.fail(
                message="unable to locate the Item"
            )

        item.delete()
