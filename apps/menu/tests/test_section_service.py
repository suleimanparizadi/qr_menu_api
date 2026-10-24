from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import time
from apps.menu.models.menu_model import QRMenu, MenuSection
from apps.menu.services import section_service


User = get_user_model()


class SectionServiceTest(TestCase):

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
        self.service = section_service.SectionService(self.user)

    def test_create_section_success(self):
        result = self.service.create_section(
            menu_id=self.menu.id,
            name='Breakfast',
            start_time=time(7, 0),
            end_time=time(11, 0),
            order=0
        )

        self.assertTrue(result.success)
        self.assertTrue(
            MenuSection.objects.filter(
                menu=self.menu,
                name='Breakfast'
            ).exists()
        )

    def test_create_section_nonexistent_menu(self):
        result = self.service.create_section(
            menu_id=99999,
            name='Breakfast'
        )

        self.assertFalse(result.success)
        self.assertIn('unable', result.message.lower())

    def test_create_section_other_users_menu(self):
        other_user = User.objects.create_user(
            phone_number='09999999999',
            display_name='patrick',
            password='securepass123'
        )
        other_menu = QRMenu.objects.create(
            user=other_user,
            title='Other Menu'
        )

        result = self.service.create_section(
            menu_id=other_menu.id,
            name='Breakfast'
        )

        self.assertFalse(result.success)

    def test_delete_section_success(self):
        section = MenuSection.objects.create(
            menu=self.menu,
            name='Breakfast'
        )

        result = self.service.delete_section(section.id)

        self.assertTrue(result.success)
        self.assertFalse(MenuSection.objects.filter(id=section.id).exists())

    def test_delete_nonexistent_section(self):
        result = self.service.delete_section(99999)

        self.assertFalse(result.success)

    def test_delete_section_cascades_items(self):
        # Import MenuItem here to avoid circular imports
        from apps.menu.models.menu_model import MenuItem

        section = MenuSection.objects.create(
            menu=self.menu,
            name='Breakfast'
        )
        item = MenuItem.objects.create(
            section=section,
            item='Omelette',
            price=150000
        )

        result = self.service.delete_section(section.id)

        self.assertTrue(result.success)
        self.assertFalse(MenuItem.objects.filter(id=item.id).exists())