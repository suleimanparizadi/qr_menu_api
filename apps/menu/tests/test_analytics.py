from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.menu.models.menu_model import QRMenu, MenuView
from apps.menu.services import analytics


User = get_user_model()


class MenuAnalyticsServiceTest(TestCase):

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
        self.service = analytics.MenuAnalyticsService(self.user)

    def test_analytics_no_views(self):
        result = self.service.get_analytics(self.menu.id)

        self.assertTrue(result.success)
        self.assertEqual(result.data['total_views'], 0)
        self.assertEqual(result.data['today_views'], 0)

    def test_analytics_with_views(self):
        for _ in range(5):
            MenuView.objects.create(menu=self.menu)

        result = self.service.get_analytics(self.menu.id)

        self.assertTrue(result.success)
        self.assertEqual(result.data['total_views'], 5)
        self.assertEqual(result.data['today_views'], 5)

    def test_analytics_menu_not_found(self):
        result = self.service.get_analytics(99999)

        self.assertFalse(result.success)

    def test_analytics_other_users_menu(self):
        other_user = User.objects.create_user(
            phone_number='09999999999',
            display_name='patrick',
            password='securepass123'
        )
        other_menu = QRMenu.objects.create(
            user=other_user,
            title='Other Menu'
        )
        other_service = analytics.MenuAnalyticsService(self.user)

        result = other_service.get_analytics(other_menu.id)

        self.assertFalse(result.success)

    def test_analytics_custom_days(self):
        for _ in range(3):
            MenuView.objects.create(menu=self.menu)

        result = self.service.get_analytics(self.menu.id, days=30)

        self.assertTrue(result.success)
        self.assertEqual(result.data['days_analytics'], 30)
        self.assertEqual(result.data['total_views'], 3)