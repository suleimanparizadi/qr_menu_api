import random

from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from apps.accounts.models.otp_models import OTP



class OTPService:

    OTP_MIN = 111111
    OTP_MAX = 999999
    EXPIRY_TIME = OTP.EXPIRY_MINUTES          
    MAX_ATTEMPT = 3
    COOLDOWN_SECONDS = 60

    def __init__(self, phone_number):
        self.phone_number = phone_number

    def generate_code(self):
        return random.randint(self.OTP_MIN, self.OTP_MAX)

    def send_otp(self, code):
        """
        Send OTP via SMS.
        Integrate with the SMS provider here.
        """
        # just for developer:
        print(f"the OTP for {self.phone_number} is {code}")

        # return True or False based on SMS sending success
        return True

    def can_request_otp(self):
        """
        Check if user can request a new OTP.
        forces cooldown period to prevent abuse.
        """
        recent_request = (
            OTP.objects.filter(
                phone_number=self.phone_number,
                created_at__gte=timezone.now() - timedelta(seconds=self.COOLDOWN_SECONDS),
            )
            .order_by("-created_at")
            .first()
        )

        if recent_request:
            wait_time = self.COOLDOWN_SECONDS - int(
                (timezone.now() - recent_request.created_at).total_seconds()
            )
            return False, max(wait_time, 0)

        return True, 0



    def create_otp(self):

 
        can_request, wait_time = self.can_request_otp()

        if not can_request:
            return False, f"Please wait {wait_time} seconds before requesting a new OTP."

       
        code = self.generate_code()
        
        OTP.objects.update_or_create(
            phone_number=self.phone_number,
            defaults={
                "code": code,
                "attempts": 0,
                "created_at": timezone.now(),
                "expired_at": timezone.now() + timedelta(minutes=self.EXPIRY_TIME),
            },
        )

        send_sms = self.send_otp(code)
        if not send_sms:
            OTP.objects.filter(phone_number=self.phone_number).delete()
            return False, "Failed to send OTP"

        
        return True, "OTP sent successfully."
      

    @transaction.atomic
    def verify_otp(self, input_code):
        if not input_code:
            return False, "code is required."

        try:
            otp = OTP.objects.select_for_update().get(phone_number=self.phone_number)
        except OTP.DoesNotExist:
            return False, "No active verification code found. Please request a new one."

        if otp.is_expired():
            otp.delete()
            return False, "the one time password is expired."

        try:
            input_code = int(input_code)
        except (ValueError, TypeError):
            return False, "Invalid format."

        if otp.code != input_code:
            otp.attempts += 1

            if otp.attempts >= self.MAX_ATTEMPT:
                otp.delete()
                return False, "Too many failed attempts. Please request a new OTP."

            otp.save(update_fields=["attempts"])
            return False, "Invalid code, try again."


     
        otp.delete()
        return True, "One time password verified successfully."




    @classmethod  # to effect the whole class 
                  # not need instance 
    def cleanup_expired(cls):
        expired_count, _ = OTP.objects.filter(expired_at__lt=timezone.now()).delete()
        return expired_count 