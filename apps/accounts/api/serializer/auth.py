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
    code = serializers.CharField(
        max_length=6,
        validators=[OTPCodeValidator()]
    )


class InitiateRegistrationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=11,
        validators=[PhoneNumberValidator()]
    )
    first_name = serializers.CharField(max_length=125)
    last_name = serializers.CharField(max_length=125)
    password = serializers.CharField(write_only=True, min_length=4,
                                     validators=[PasswordValidator()])
    password_confirm = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False)
    date_of_birth = serializers.DateField(required=False)
    
    def validate_first_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("First name is required")
        return value.strip()
    
    def validate_last_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Last name is required")
        return value.strip()
    
    def validate(self, data):
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': "Passwords must match."
            })
        data.pop('password_confirm', None)
        return data


class AdminUserSerializer(serializers.ModelSerializer):

    class Meta:

        model = User
        fields = [
            'id', 'phone_number', 'first_name', 'last_name',
            'email', 'is_active', 'is_admin', 'date_of_birth',
            'created_at', 'last_login_at'
        ]
        read_only_fields = ['id', 'created_at', 'last_login_at']