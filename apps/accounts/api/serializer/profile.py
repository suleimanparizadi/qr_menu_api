from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.accounts.api.serializer.validators import PasswordValidator
from django.core.exceptions import ValidationError


User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = [
            'phone_number', 
            'first_name', 
            'last_name', 
            'email',
            'date_of_birth',
            'created_at',
            'last_login_at',
            'is_admin'
        ]
        read_only_fields = ['phone_number', 'created_at',
                             'last_login_at']
      

      

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8, 
                                         validators=[PasswordValidator()])
    confirm_password = serializers.CharField(write_only=True)



    def validate(self, attrs):
        if attrs.get('new_password') != attrs.get('confirm_password'):
            raise ValidationError(
                {'confirm_password': "Passwords do not match."}
            )
        return attrs