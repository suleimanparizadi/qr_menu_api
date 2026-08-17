from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.accounts.services.registration import InitiateRegister
from apps.accounts.models.otp_models import OTP
from apps.accounts.services.otp import OTPService 
from unittest.mock import patch



User = get_user_model() 


class RegistrationServiceTest(TestCase):
    
    def setUp(self):
        self.phone_number = '09123456789'
        self.service = InitiateRegister(self.phone_number)
        self.valid_data = {
            'display_name': 'spongebob',
            'password': 'securepass123',
        }
        
    def test_initiate_registration_success(self):
        
        service = self.service
        result = service.initiate_register(**self.valid_data)

        self.assertTrue(result.success)
        self.assertIn('sent successfully', result.message.lower())

        self.assertTrue(OTP.objects.filter(phone_number=self.phone_number).exists())


      
    def test_initiate_registration_duplicate_phone(self):
        User.objects.create_user(phone_number=self.phone_number, **self.valid_data)
        
        service = self.service
        result = service.initiate_register(**self.valid_data)

        self.assertFalse(result.success)
        self.assertIn('already', result.message.lower())



    @patch.object(OTPService, 'send_otp', return_value=True)
    def test_verify_and_create_user_success(self, mock_send):
        self.service.initiate_register(**self.valid_data)
        otp = OTP.objects.get(phone_number=self.phone_number)
        
        result = self.service.verify_and_create_user(
            code=str(otp.code),
            display_name=self.valid_data['display_name'],
            password=self.valid_data['password']
        )

        self.assertTrue(result.success)
        self.assertTrue(User.objects.filter(phone_number=self.phone_number).exists())
        self.assertIn('token', result.data)



    def test_verify_and_create_user_duplicate(self):
        User.objects.create_user(
            phone_number=self.phone_number,
            display_name='Existing',
            password='ExistingPass123'
        )
        
        result = self.service.verify_and_create_user(
            code='123456',  
            display_name='New',
            password='NewPass123'
        )       


        self.assertFalse(result.success)
        self.assertIn('already', result.message.lower())