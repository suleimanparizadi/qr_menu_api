from apps.accounts.models.otp_models import OTP
import random
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from utils.service_result import ServiceResult  


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
            return ServiceResult.fail(
                message=f"Please wait {max(wait_time, 0)} seconds before requesting a new OTP.",
                code="COOLDOWN_ACTIVE"
            )

        return ServiceResult.success(message="Can request OTP")



    def create_otp(self):
        can_request_result = self.can_request_otp()
        if not can_request_result.success:
            return can_request_result

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

        if send_sms:
            return ServiceResult.success(
                message="OTP sent successfully.",
                data={"phone_number": self.phone_number}
            )
        else:
            OTP.objects.filter(phone_number=self.phone_number).delete()
            return ServiceResult.fail(
                message="Failed to send OTP. Please try again later.",
                code="SMS_SEND_FAILED"
            )




    @transaction.atomic
    def verify_otp(self, input_code):

        # Validate input
        if not input_code:
            return ServiceResult.fail(
                message="Code is required.",
                code="INVALID_INPUT"
            )

        # Fetch OTP from database
        try:
            otp = OTP.objects.select_for_update().get(phone_number=self.phone_number)
        except OTP.DoesNotExist:
            return ServiceResult.fail(
                message="No active verification code found. Please request a new one.",
                code="OTP_NOT_FOUND"
            )

        # Check if OTP is expired
        if otp.is_expired():
            otp.delete()
            return ServiceResult.fail(
                message="The one time password is expired.",
                code="OTP_EXPIRED"
            )

        # Validate input format
        try:
            input_code = int(input_code)
        except (ValueError, TypeError):
            return ServiceResult.fail(
                message="Invalid format. Please enter a numeric code.",
                code="INVALID_FORMAT"
            )

        # Verify code
        if otp.code != input_code:
            otp.attempts += 1

            # Check if max attempts reached
            if otp.attempts >= self.MAX_ATTEMPT:
                otp.delete()
                return ServiceResult.fail(
                    message="Too many failed attempts. Please request a new OTP.",
                    code="MAX_ATTEMPTS_EXCEEDED"
                )

            otp.save(update_fields=["attempts"])
            remaining_attempts = self.MAX_ATTEMPT - otp.attempts
            return ServiceResult.fail(
                message=f"Invalid code, try again. {remaining_attempts} attempts remaining.",
                code="INVALID_CODE"
            )

        # Success - code matched
        otp.delete()
        return ServiceResult.success(
            message="One time password verified successfully.",
            data={"phone_number": self.phone_number}
        )



    @classmethod
    def cleanup_expired(cls):
        """
        Clean up all expired OTPs from the database.
        """
        expired_count, _ = OTP.objects.filter(expired_at__lt=timezone.now()).delete()
        
        if expired_count > 0:
            return ServiceResult.success(
                message=f"Successfully cleaned up {expired_count} expired OTPs.",
                data={"deleted_count": expired_count}
            )

        
        else:
            return ServiceResult.success(
                message="No expired OTPs found to clean up.",
                data={"deleted_count": 0}
            )