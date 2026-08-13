from rest_framework import serializers
from .validators import PhoneNumberValidator, OTPCodeValidator, PasswordValidator
from django.contrib.auth import get_user_model


User = get_user_model()



class PasswordLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=11,
        validators=[PhoneNumberValidator()]
    )
    password = serializers.CharField(write_only=True)


class SendLoginOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=11,
        validators=[PhoneNumberValidator()]
    )


class VerifyLoginOTPSerializer(serializers.Serializer):


    phone_number = serializers.CharField(
        max_length=11,
        validators=[PhoneNumberValidator()]
    )  
    code = serializers.IntegerField(
        max_length=6,
    )


class InitiateRegistrationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=11,
        validators=[PhoneNumberValidator()]
    )
    display_name = serializers.CharField(max_length=125)
    password = serializers.CharField(write_only=True, min_length=6,
                                     validators=[PasswordValidator()])
    password_confirm = serializers.CharField(write_only=True)
    
    def validate_display_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("display_name name is required")
        return value.strip()
   
    def validate(self, data):
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': "Passwords must match."
            })
        data.pop('password_confirm', None)
        return data


class UserSerializer(serializers.ModelSerializer):

    class Meta:

        model = User
        fields = [
            'id', 'phone_number', 'display_name','is_active','created_at', 
        ]
        read_only_fields = ['id', 'created_at']