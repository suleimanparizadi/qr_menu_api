from django.db import transaction, IntegrityError
from django.contrib.auth import get_user_model
from apps.accounts.services.otp import OTPService


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
            return False, "this phone number is already registered"

        if not display_name:
            return False, "display_name is required"    

        if not password:
            return False, "password is required"    


        success, message = self.otp.create_otp()

        return success, message


    def verify_and_create_user(self, code, display_name, password):

        success, message = self.otp.verify_otp(code)

        if not success:
            return False, "Unable to create user"


        try:            
            user = User.objects.create_user(
                phone_number=self.phone_number,
                display_name=display_name,
                password=password
            )

            return user, message

        except IntegrityError:
            return False ,'A user is already registered with this phone number'



             
