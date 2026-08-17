from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.accounts.services.login import PasswordLoginService, OTPLoginService
from apps.accounts.models.otp_models import OTP
from apps.accounts.services.otp import OTPService
from unittest.mock import patch
from rest_framework.authtoken.models import Token


User = get_user_model()


class PasswordLoginServiceTest(TestCase):
    
    def setUp(self):
        self.phone_number = '09123456789'
        self.password = 'securepass123'
        self.user = User.objects.create_user(
            phone_number=self.phone_number,
            display_name='spongebob',
            password=self.password
        )

    
    def test_login_success(self):
        service = PasswordLoginService(self.phone_number, self.password)
        result = service.login()
        
        self.assertTrue(result.success)
        self.assertIn('token', result.data)


    def test_login_invalid_phone(self):
        service = PasswordLoginService('09999999999', self.password)
        result = service.login()
        
        self.assertFalse(result.success)
        self.assertEqual(result.message, 'Invalid phone number or password.')

    
    def test_login_invalid_password(self):
        service = PasswordLoginService(self.phone_number, 'wrongpass')
        result = service.login()
        
        self.assertFalse(result.success)
        self.assertEqual(result.message, 'Invalid phone number or password.')

    
    def test_login_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        
        service = PasswordLoginService(self.phone_number, self.password)
        result = service.login()
        
        self.assertFalse(result.success)
        self.assertEqual(result.message, 'Invalid phone number or password.')



class OTPLoginServiceTest(TestCase):
    
    def setUp(self):
        self.phone_number = '09123456789'
        self.user = User.objects.create_user(
            phone_number=self.phone_number,
            display_name='spongebob',
            password='securepass123'
        )

    
    @patch.object(OTPService, 'create_otp')
    def test_send_otp_success(self, mock_create):
        mock_create.return_value = type('ServiceResult', (), {
            'success': True,
            'message': 'OTP sent successfully.',
            'data': {'phone_number': self.phone_number}
        })()
        
        service = OTPLoginService(self.phone_number)
        result = service.send_otp()
        
        self.assertTrue(result.success)
        self.assertEqual(result.message, 'OTP sent successfully.')

    
    @patch.object(OTPService, 'create_otp')
    def test_send_otp_user_not_found(self, mock_create):
        service = OTPLoginService('09999999999')
        result = service.send_otp()
        
        self.assertFalse(result.success)
        self.assertEqual(result.message, 'Unable to process request. Please try again later.')
        mock_create.assert_not_called()


    
    @patch.object(OTPService, 'verify_otp')
    def test_verify_otp_success(self, mock_verify):
        mock_verify.return_value = type('ServiceResult', (), {
            'success': True,
            'message': 'One time password verified successfully.',
            'data': {'phone_number': self.phone_number}
        })()
        
        service = OTPLoginService(self.phone_number)
        result = service.verify_otp('123456')
        
        self.assertTrue(result.success)
        self.assertIn('token', result.data)


    
    @patch.object(OTPService, 'verify_otp')
    def test_verify_otp_invalid_code(self, mock_verify):
        mock_verify.return_value = type('ServiceResult', (), {
            'success': False,
            'message': 'Invalid code',
            'data': None
        })()
        
        service = OTPLoginService(self.phone_number)
        result = service.verify_otp('999999')
        
        self.assertFalse(result.success)
        self.assertEqual(result.message, 'Invalid code')


    
    @patch.object(OTPService, 'verify_otp')
    def test_verify_otp_user_not_found(self, mock_verify):
        mock_verify.return_value = type('ServiceResult', (), {
            'success': True,
            'message': 'Verified',
            'data': {'phone_number': '09999999999'}
        })()
        
        service = OTPLoginService('09999999999')
        result = service.verify_otp('123456')
        
        self.assertFalse(result.success)
        self.assertEqual(result.message, 'Accounts not found')



    
    @patch.object(OTPService, 'create_otp')
    def test_send_otp_user_not_active(self, mock_create):
        self.user.is_active = False
        service = OTPLoginService('09876543210')
        result = service.send_otp()

        self.assertFalse(result.success)
        self.assertIn('Unable to process', result.success)


     