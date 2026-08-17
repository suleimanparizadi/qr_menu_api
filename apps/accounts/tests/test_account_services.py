from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.accounts.services.registration import Account, ChangePhone_number
from apps.accounts.services.otp import OTPService
from rest_framework.authtoken.models import Token
from unittest.mock import patch


User = get_user_model()


class AccountServiceTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            phone_number='09123456789',
            display_name='spongebob',
            password='securepass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.account_service = Account(self.user)

    
    def test_logout_success(self):
        result = self.account_service.logout()
        
        self.assertTrue(result.success)
        self.assertEqual(result.message, 'User been logged out.')
        self.assertFalse(Token.objects.filter(user=self.user).exists())


    
    def test_changing_display_name_success(self):
        result = self.account_service.changing_display_name('New Name')
        
        self.assertTrue(result.success)
        self.assertEqual(result.message, 'Display name changed')
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.display_name, 'New Name')




class ChangePhoneNumberServiceTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            phone_number='09123456789',
            display_name='spongebob',
            password='securepass123'
        )
        self.new_phone = '09123456788'
        self.service = ChangePhone_number(self.user, self.new_phone)


    
    @patch.object(OTPService, 'create_otp')
    def test_send_otp_success(self, mock_create):
        mock_create.return_value = type('ServiceResult', (), {
            'success': True,
            'message': 'OTP sent successfully.',
            'data': {'phone_number': self.new_phone}
        })()
        
        result = self.service.send_otp()
        
        self.assertTrue(result.success)
        self.assertEqual(result.message, 'OTP sent successfully.')


    
    @patch.object(OTPService, 'create_otp')
    def test_send_otp_phone_already_exists(self, mock_create):
        # Create another user with the new phone number
        User.objects.create_user(
            phone_number=self.new_phone,
            display_name='existing',
            password='pass123'
        )
        
        result = self.service.send_otp()
        
        self.assertFalse(result.success)
        self.assertEqual(result.message, 'This phone number is already registered.')
        mock_create.assert_not_called()



    
    @patch.object(OTPService, 'verify_otp')
    def test_verify_otp_success(self, mock_verify):
        mock_verify.return_value = type('ServiceResult', (), {
            'success': True,
            'message': 'OTP verified successfully.',
            'data': {'phone_number': self.new_phone}
        })()
        
        result = self.service.Verify_otp('123456')
        
        self.assertTrue(result.success)
        self.assertEqual(result.message, 'phone number changed successfully')
        self.assertEqual(result.data['phone_number'], self.new_phone)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone_number, self.new_phone)



    
    @patch.object(OTPService, 'verify_otp')
    def test_verify_otp_invalid_code(self, mock_verify):
        mock_verify.return_value = type('ServiceResult', (), {
            'success': False,
            'message': 'Invalid code',
            'data': None
        })()
        
        result = self.service.Verify_otp('999999')
        
        self.assertFalse(result.success)
        self.assertEqual(result.message, 'Invalid code')
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone_number, '09123456789')  # Not changed



    
    @patch.object(OTPService, 'verify_otp')
    def test_verify_otp_phone_already_exists(self, mock_verify):
        mock_verify.return_value = type('ServiceResult', (), {
            'success': True,
            'message': 'OTP verified successfully.',
            'data': {'phone_number': self.new_phone}
        })()
        
        # Create another user with the new phone number
        User.objects.create_user(
            phone_number=self.new_phone,
            display_name='existing',
            password='pass123'
        )
        
        result = self.service.Verify_otp('123456')
        
        self.assertFalse(result.success)
        self.assertEqual(result.message, 'This phone number is already registered.')