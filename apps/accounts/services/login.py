from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from apps.accounts.services.otp import OTPService
from utils.normalizing_phone import normalize_phone
from utils.service_result import ServiceResult


User = get_user_model()



class PasswordLoginService:

    """
        Handles phone number + password login.
        Returns JWT tokens on success.
        """


    def __init__(self, phone_number, password):
        self.phone_number = normalize_phone(phone_number)
        self.password = password



    def login(self):

        try:
            user = User.objects.get(phone_number=self.phone_number)        
       
        except User.DoesNotExist:
            return ServiceResult.fail(
                message="Invalid phone number or password."
            )
        
        if not user.is_active:
            return ServiceResult.fail(
                message="Invalid phone number or password."
                )        

        if not user.check_password(self.password):
            return ServiceResult.fail(
                message="Invalid phone number or password."
                )            
        

        token, _ = Token.objects.get_or_create(user=user)
       
        return ServiceResult.success(
            data={'token':token.key},
            message= "you logged in successfully!"
        )
    


class OTPLoginService:

    def __init__(self, phone_number):
        self.phone_number = normalize_phone(phone_number)



    def send_otp(self):

        if  User.objects.filter(phone_number=self.phone_number, is_active=True).exists():

            otp_service = OTPService(self.phone_number)

            result = otp_service.create_otp()

            if result.success:           
                return ServiceResult.success(
                    message=result.message
                )

        return ServiceResult.fail(
            message="Unable to process request. Please try again later."
        )
            

    def verify_otp(self, input_code):


        otp_service = OTPService(self.phone_number)
        result = otp_service.verify_otp(input_code)


        if result.success:

            try:
                user = User.objects.get(phone_number=self.phone_number, is_active=True)
            except User.DoesNotExist:
                return ServiceResult.fail(
                    message="Accounts not found"
                )
            
            token, _ = Token.objects.get_or_create(user=user)
           
            return ServiceResult.success(
                data={'token':token.key},
                message=result.message
            )
        
        return ServiceResult.fail(
            message=result.message
        )


    