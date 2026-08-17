from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from unittest.mock import patch
from apps.accounts.services.otp import OTPService



User = get_user_model()




class RegistrationViewTest(TestCase):


    
    def setUp(self):
        self.client = APIClient()
        self.phone_number = '09123456789'
        self.display_name = 'spongebob'
        self.password = 'securepass123'



    
    @patch.object(OTPService, 'create_otp')
    def test_initiate_registration_success(self, mock_create):
        mock_create.return_value = type('ServiceResult', (), {
            'success': True,
            'message': 'OTP sent successfully.'
        })()
        
        response = self.client.post('/api/accounts/register/', {
            'phone_number': self.phone_number,
            'display_name': self.display_name,
            'password': self.password
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'OTP sent successfully.')


    
    @patch.object(OTPService, 'create_otp')
    def test_initiate_registration_duplicate(self, mock_create):
        User.objects.create_user(
            phone_number=self.phone_number,
            display_name=self.display_name,
            password=self.password
        )
        
        response = self.client.post('/api/accounts/register/', {
            'phone_number': self.phone_number,
            'display_name': self.display_name,
            'password': self.password
        })
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('already', response.data['message'].lower())


    
    @patch.object(OTPService, 'verify_otp')
    def test_verify_registration_success(self, mock_verify):
        # Setup session
        session = self.client.session
        session['user_register_session'] = {
            'display_name': self.display_name,
            'phone_number': self.phone_number,
            'password': self.password
        }
        session.save()
        
        mock_verify.return_value = type('ServiceResult', (), {
            'success': True,
            'message': 'Verified',
            'data': {'phone_number': self.phone_number}
        })()
        
        response = self.client.post('/api/accounts/verify/', {'code': '123456'})
        
        self.assertEqual(response.status_code, 201)
        self.assertIn('token', response.data)



    
    def test_verify_registration_no_session(self):
        response = self.client.post('/api/accounts/verify/', {'code': '123456'})
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'], 'unable to find user session. start over!')





class LoginViewTest(TestCase):



    def setUp(self):
        self.client = APIClient()
        self.phone_number = '09123456789'
        self.password = 'securepass123'
        self.user = User.objects.create_user(
            phone_number=self.phone_number,
            display_name='spongebob',
            password=self.password
        )
    
    def test_login_password_success(self):
        response = self.client.post('/api/accounts/login/password/', {
            'phone_number': self.phone_number,
            'password': self.password
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
    
    def test_login_password_fail(self):
        response = self.client.post('/api/accounts/login/password/', {
            'phone_number': self.phone_number,
            'password': 'wrongpass'
        })
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'], 'Invalid phone number or password.')
    
    @patch.object(OTPService, 'create_otp')
    def test_send_login_otp_success(self, mock_create):
        mock_create.return_value = type('ServiceResult', (), {
            'success': True,
            'message': 'OTP sent successfully.'
        })()
        
        response = self.client.post('/api/accounts/login/send_otp/', {
            'phone_number': self.phone_number
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'OTP sent successfully.')
    
    @patch.object(OTPService, 'create_otp')
    def test_send_login_otp_user_not_found(self, mock_create):
        response = self.client.post('/api/accounts/login/send_otp/', {
            'phone_number': '09999999999'
        })
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'], 'Unable to process request. Please try again later.')
        mock_create.assert_not_called()
    
    @patch.object(OTPService, 'verify_otp')
    def test_verify_login_otp_success(self, mock_verify):
        mock_verify.return_value = type('ServiceResult', (), {
            'success': True,
            'message': 'Verified',
            'data': {'phone_number': self.phone_number}
        })()
        
        response = self.client.post('/api/accounts/login/verify/', {
            'phone_number': self.phone_number,
            'code': '123456'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
    
    @patch.object(OTPService, 'verify_otp')
    def test_verify_login_otp_invalid(self, mock_verify):
        mock_verify.return_value = type('ServiceResult', (), {
            'success': False,
            'message': 'Invalid code'
        })()
        
        response = self.client.post('/api/accounts/login/verify/', {
            'phone_number': self.phone_number,
            'code': '999999'
        })
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'], 'Invalid code')



class AuthenticatedViewTest(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            phone_number='09123456789',
            display_name='spongebob',
            password='securepass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')


    def test_logout_success(self):
        response = self.client.post('/api/accounts/logout/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'User been logged out.')
        self.assertFalse(Token.objects.filter(user=self.user).exists())


    def test_profile_success(self):
        response = self.client.get('/api/accounts/profile/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['phone_number'], self.user.phone_number)



    def test_change_display_name_success(self):
        response = self.client.post('/api/accounts/change/name/', {
            'display_name': 'New Name'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Display name changed')
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.display_name, 'New Name')



    @patch.object(OTPService, 'create_otp')
    def test_change_phone_send_otp_success(self, mock_create):
        mock_create.return_value = type('ServiceResult', (), {
            'success': True,
            'message': 'OTP sent successfully.'
        })()
        
        response = self.client.post('/api/accounts/change/phone/send_otp/', {
            'new_phone_number': '09123456788'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'OTP sent successfully.')




    @patch.object(OTPService, 'create_otp')
    def test_change_phone_send_otp_already_exists(self, mock_create):
        User.objects.create_user(
            phone_number='09123456788',
            display_name='existing',
            password='pass123'
        )
        
        response = self.client.post('/api/accounts/change/phone/send_otp/', {
            'new_phone_number': '09123456788'
        })
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'], 'This phone number is already registered.')
        mock_create.assert_not_called()





    @patch.object(OTPService, 'verify_otp')
    def test_change_phone_verify_success(self, mock_verify):
        mock_verify.return_value = type('ServiceResult', (), {
            'success': True,
            'message': 'Verified',
            'data': {'phone_number': '09123456788'}
        })()
        
        response = self.client.post('/api/accounts/change/phone/verify_otp/', {
            'phone_number': '09123456788',
            'code': '123456'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'phone number changed successfully')
        self.assertEqual(response.data['new_phone_number'], '09123456788')




    @patch.object(OTPService, 'verify_otp')
    def test_change_phone_verify_invalid(self, mock_verify):
        mock_verify.return_value = type('ServiceResult', (), {
            'success': False,
            'message': 'Invalid code'
        })()
        
        response = self.client.post('/api/accounts/change/phone/verify_otp/', {
            'phone_number': '09123456788',
            'code': '999999'
        })
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'], 'Invalid code')





class UnauthenticatedViewTest(TestCase):
    """Test that authenticated views reject unauthenticated requests"""
    
    def setUp(self):
        self.client = APIClient()



    def test_logout_requires_auth(self):
        response = self.client.post('/api/accounts/logout/')
        self.assertEqual(response.status_code, 401)



    def test_profile_requires_auth(self):
        response = self.client.get('/api/accounts/profile/')
        self.assertEqual(response.status_code, 401)



    def test_change_name_requires_auth(self):
        response = self.client.post('/api/accounts/change/name/', {
            'display_name': 'New Name'
        })
        self.assertEqual(response.status_code, 401)



    def test_change_phone_send_otp_requires_auth(self):
        response = self.client.post('/api/accounts/change/phone/send_otp/', {
            'new_phone_number': '09123456788'
        })
        self.assertEqual(response.status_code, 401)



    def test_change_phone_verify_requires_auth(self):
        response = self.client.post('/api/accounts/change/phone/verify_otp/', {
            'phone_number': '09123456788',
            'code': '123456'
        })
        self.assertEqual(response.status_code, 401)