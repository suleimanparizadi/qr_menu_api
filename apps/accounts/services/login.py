from django.contrib.auth import get_user_model
from apps.accounts.services.otp import OTPService
from utils.normalizing_phone import normalize_phone


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
            return False, "Invalid phone number or password."        
        
        if not user.is_active:
            return False, "Invalid phone number or password."
        

        if not user.check_password(self.password):
            return False, "Invalid phone number or password."
        

        

        return user, "you logged in successfully!"
    


class OTPLoginService:

    def __init__(self, phone_number):
        self.phone_number = normalize_phone(phone_number)



    def send_otp(self):

        if  User.objects.filter(phone_number=self.phone_number, is_active=True).exists():

            otp_service = OTPService(self.phone_number)

            success, message = otp_service.create_otp()
           
            return success, message
      
        return False, "Unable to process request. Please try again later."
            

    def verify_otp(self, input_code):


        otp_service = OTPService(self.phone_number)
        success, message = otp_service.verify_otp(input_code)


        if success:

            try:
                user = User.objects.get(phone_number=self.phone_number, is_active=True)
            except User.DoesNotExist:
                return False, "Accounts not found"
            
            
            return user, message
        
        return False, message