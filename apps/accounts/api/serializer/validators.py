from rest_framework import serializers
import re


class PhoneNumberValidator:

    
    MESSAGE = "Phone number must be in format: 09xxxxxxxxx"
    REGEX = r'^09\d{9}$'
    
    def __call__(self, value):
        if not re.match(self.REGEX, value):
            raise serializers.ValidationError(self.MESSAGE)
        return value


class PasswordValidator:

    
    MESSAGE = "Password must be at least 4 characters with letters and numbers"
    
    def __call__(self, value):
        if len(value) < 4:
            raise serializers.ValidationError("Password must be at least 4 characters")
        if not re.search(r'[A-Za-z]', value):
            raise serializers.ValidationError("Password must contain at least one letter")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one number")
        return value


class OTPCodeValidator:
    """
    Reusable OTP code validator.
    """
    
    def __call__(self, value):
        if not value:
            raise serializers.ValidationError("Code is required")
        if not str(value).isdigit():
            raise serializers.ValidationError("Code must contain only digits")
        if len(str(value)) != 6:
            raise serializers.ValidationError("Code must be 6 digits")
        return value