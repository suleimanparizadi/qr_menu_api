from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.menu.models.menu_model import QRMenu, MenuSection, MenuItem
from apps.menu.services import item_service


User = get_user_model()


class ItemServiceTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            phone_number='09123456789',
            display_name='spongebob',
            password='securepass123'
        )
        self.menu = QRMenu.objects.create(
            user=self.user,
            title='My Restaurant'
        )
        self.section = MenuSection.objects.create(
            menu=self.menu,
            name='Main'
        )
        self.service = item_service.ItemService(self.user)

    def test_add_single_item(self):
        result = self.service.add_items(
            section_id=self.section.id,
            items_data=[
                {'item': 'Omelette', 'description': 'Three-egg', 'price': 150000}
            ]
        )

        self.assertTrue(result.success)
        self.assertEqual(result.data['items_count'], 1)
        self.assertEqual(self.section.items.count(), 1)

    def test_add_multiple_items(self):
        result = self.service.add_items(
            section_id=self.section.id,
            items_data=[
                {'item': 'Omelette', 'price': 150000},
                {'item': 'Toast', 'price': 50000},
                {'item': 'Coffee', 'price': 35000},
            ]
        )

        self.assertTrue(result.success)
        self.assertEqual(result.data['items_count'], 3)
        self.assertEqual(self.section.items.count(), 3)

    def test_add_items_nonexistent_section(self):
        result = self.service.add_items(
            section_id=99999,
            items_data=[{'item': 'Omelette', 'price': 150000}]
        )

        self.assertFalse(result.success)

    def test_add_items_other_users_section(self):
        other_user = User.objects.create_user(
            phone_number='09999999999',
            display_name='patrick',
            password='securepass123'
        )
        other_menu = QRMenu.objects.create(
            user=other_user,
            title='Other Menu'
        )
        other_section = MenuSection.objects.create(
            menu=other_menu,
            name='Main'
        )

        result = self.service.add_items(
            section_id=other_section.id,
            items_data=[{'item': 'Hack', 'price': 0}]
        )

        self.assertFalse(result.success)

    def test_add_items_sets_default_order(self):
        result = self.service.add_items(
            section_id=self.section.id,
            items_data=[
                {'item': 'First', 'price': 100},
                {'item': 'Second', 'price': 200},
                {'item': 'Third', 'price': 300},
            ]
        )

        self.assertTrue(result.success)

        items = list(self.section.items.order_by('order'))
        self.assertEqual(items[0].order, 0)
        self.assertEqual(items[1].order, 1)
        self.assertEqual(items[2].order, 2)

    def test_delete_item_success(self):
        item = MenuItem.objects.create(
            section=self.section,
            item='Omelette',
            price=150000
        )

        result = self.service.delete_item(item.id)

        self.assertTrue(result.success)
        self.assertFalse(MenuItem.objects.filter(id=item.id).exists())

    def test_delete_nonexistent_item(self):
        result = self.service.delete_item(99999)

        self.assertFalse(result.success)