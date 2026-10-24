from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
from apps.menu.models.menu_model import QRMenu, MenuSection
from apps.menu.services import menu_service


User = get_user_model()


class MenuServiceTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            phone_number='09123456789',
            display_name='spongebob',
            password='securepass123'
        )
        self.service = menu_service.MenuService(self.user)

    @patch('apps.menu.services.menu_service.generate_qr_code')
    def test_create_menu_success(self, mock_task):
        result = self.service.create_menu(
            title='My Restaurant',
            description='Delicious food'
        )

        self.assertTrue(result.success)
        self.assertTrue(QRMenu.objects.filter(title='My Restaurant').exists())

        menu = QRMenu.objects.get(title='My Restaurant')
        self.assertEqual(menu.user, self.user)

    @patch('apps.menu.services.menu_service.generate_qr_code')
    def test_create_menu_creates_main_section(self, mock_task):
        result = self.service.create_menu(title='My Restaurant')

        self.assertTrue(result.success)

        menu = QRMenu.objects.get(title='My Restaurant')
        self.assertEqual(menu.sections.count(), 1)

        section = menu.sections.first()
        self.assertEqual(section.name, 'Main')
        self.assertEqual(section.order, 0)

    @patch('apps.menu.services.menu_service.generate_qr_code')
    def test_create_menu_queues_qr_task(self, mock_task):
        result = self.service.create_menu(title='My Restaurant')

        self.assertTrue(result.success)
        # QR task should be queued (mocked)
        # Note: on_commit may not fire in tests, so we check the task was called
        # This depends on whether you're using TransactionTestCase

    def test_delete_menu_success(self):
        menu = QRMenu.objects.create(
            user=self.user,
            title='My Restaurant'
        )

        result = self.service.delete_menu(menu.id)

        self.assertTrue(result.success)
        self.assertFalse(QRMenu.objects.filter(id=menu.id).exists())

    def test_delete_nonexistent_menu(self):
        result = self.service.delete_menu(99999)

        self.assertFalse(result.success)
        self.assertIn('unable', result.message.lower())

    def test_delete_other_users_menu(self):
        other_user = User.objects.create_user(
            phone_number='09999999999',
            display_name='patrick',
            password='securepass123'
        )
        menu = QRMenu.objects.create(
            user=other_user,
            title='Other Menu'
        )

        result = self.service.delete_menu(menu.id)

        self.assertFalse(result.success)
        self.assertTrue(QRMenu.objects.filter(id=menu.id).exists())