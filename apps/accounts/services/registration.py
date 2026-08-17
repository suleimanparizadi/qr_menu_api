from rest_framework.authtoken.models import Token
from django.db import transaction, IntegrityError
from django.contrib.auth import get_user_model
from apps.accounts.services.otp import OTPService
from utils.service_result import ServiceResult



User = get_user_model()



class InitiateRegister:


    def __init__(self, phone_number):

        self.phone_number = phone_number
        self.otp = OTPService(phone_number)


    @transaction.atomic
    def initiate_register(self, display_name, password):

        # select_for_update() is a Pre-check for better UX. The real uniqueness guarantee is the
        # IntegrityError catch in verify_and_create_user.

         
        if User.objects.select_for_update().filter(phone_number=self.phone_number).first():
            return ServiceResult.fail(
                message="this phone number is already registered"
            )

            
        if not display_name:
            return ServiceResult.fail(
                message="display_name is required" 
            )
        if not password:
            return ServiceResult.fail(
                message="password is required"
            )

        result = self.otp.create_otp()
        return result





    def verify_and_create_user(self, code, display_name, password):

        result = self.otp.verify_otp(code)

        if not result.success:
            return ServiceResult.fail(
                message="Unable to create user"
            )


        try:            
            user = User.objects.create_user(
                phone_number=self.phone_number,
                display_name=display_name,
                password=password
            )
            token, _ = Token.objects.get_or_create(user=user)

            return ServiceResult.success(
                
                data={'token':token.key},
                message='user created successfully'
            )
            

        except IntegrityError:
            return ServiceResult.fail(
                code="IntegrityError",
                message='A user is already registered with this phone number'
            )


class Account:

    def __init__(self, user):
        self.user = user 


    def logout(self):
        
        Token.objects.get(user=self.user).delete()
        return ServiceResult.success(
            message= "User been logged out."
        )


    def changing_display_name(self, display_name):

        self.user.display_name = display_name
        self.user.save(update_fields=['display_name', 'updated_at'])
        return ServiceResult.success(
            message="Display name changed"
        )



class ChangePhone_number:

    def __init__(self, user, phone_number):

        self.phone_number = phone_number
        self.otp = OTPService(phone_number)
        self.user = user


    def send_otp(self):

        if User.objects.filter(phone_number=self.phone_number).exists():

            return ServiceResult.fail(
                message="This phone number is already registered.",
                code="PHONE_ALREADY_EXISTS"
            )

        result = self.otp.create_otp()

        return result



    def Verify_otp(self, code):

        result = self.otp.verify_otp(code)

        if User.objects.filter(phone_number=self.phone_number).exists():

            return ServiceResult.fail(
                message="This phone number is already registered.",
                code="PHONE_ALREADY_EXISTS"
            )


        if result.success:
            self.user.phone_number = self.phone_number
            self.user.save(update_fields=['phone_number', 'updated_at'])

            return ServiceResult.success(
                message="phone number changed successfully",
                data = {'phone_number': self.phone_number}
            )

        return result
        

    

        

