from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import time, timedelta
from apps.menu.models.menu_model import QRMenu, MenuSection, MenuItem, MenuView
from apps.menu.services import public_menu


User = get_user_model()


class PublicMenuServiceTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            phone_number='09123456789',
            display_name='spongebob',
            password='securepass123'
        )
        self.menu = QRMenu.objects.create(
            user=self.user,
            title='My Restaurant',
            available=True
        )

    def test_get_menu_success(self):
        MenuSection.objects.create(menu=self.menu, name='Main')

        service = public_menu.PublicMenuService()
        result = service.get_menu(self.menu.id)

        self.assertTrue(result.success)
        self.assertEqual(result.data['menu'].id, self.menu.id)

    def test_get_menu_not_found(self):
        service = public_menu.PublicMenuService()
        result = service.get_menu(99999)

        self.assertFalse(result.success)

    def test_get_menu_unavailable(self):
        self.menu.available = False
        self.menu.save()

        service = public_menu.PublicMenuService()
        result = service.get_menu(self.menu.id)

        self.assertFalse(result.success)

    def test_get_menu_records_view(self):
        MenuSection.objects.create(menu=self.menu, name='Main')

        service = public_menu.PublicMenuService()
        service.get_menu(self.menu.id)

        self.assertEqual(MenuView.objects.filter(menu=self.menu).count(), 1)

    def test_get_menu_filters_by_time(self):
        now = timezone.localtime().time()
        current_hour = now.hour

        # Create a section active right now
        active_section = MenuSection.objects.create(
            menu=self.menu,
            name='Active',
            start_time=time(current_hour, 0),
            end_time=time(current_hour, 59),
            order=0
        )

        # Create a section that is NOT active now
        inactive_section = MenuSection.objects.create(
            menu=self.menu,
            name='Inactive',
            start_time=time((current_hour + 2) % 24, 0),
            end_time=time((current_hour + 3) % 24, 0),
            order=1
        )

        service = public_menu.PublicMenuService()
        result = service.get_menu(self.menu.id)

        self.assertTrue(result.success)

        sections = result.data['sections']
        section_names = [s.name for s in sections]

        self.assertIn('Active', section_names)
        self.assertNotIn('Inactive', section_names)

    def test_get_menu_includes_always_visible_sections(self):
        MenuSection.objects.create(
            menu=self.menu,
            name='Drinks',
            start_time=None,
            end_time=None
        )

        service = public_menu.PublicMenuService()
        result = service.get_menu(self.menu.id)

        self.assertTrue(result.success)
        self.assertEqual(len(result.data['sections']), 1)
        self.assertEqual(result.data['sections'][0].name, 'Drinks')

    def test_get_menu_no_active_sections(self):
        now = timezone.localtime().time()
        current_hour = now.hour

        # Section only active during hours that are NOT now
        MenuSection.objects.create(
            menu=self.menu,
            name='Closed',
            start_time=time((current_hour + 2) % 24, 0),
            end_time=time((current_hour + 3) % 24, 0)
        )

        service = public_menu.PublicMenuService()
        result = service.get_menu(self.menu.id)

        self.assertFalse(result.success)
        self.assertIn('unavailable', result.message.lower())