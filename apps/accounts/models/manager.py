import re

from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError





class UserManager(BaseUserManager):

    def _create_user(self , phone_number, display_name, password=None, **extra_fields):
     
        if not phone_number:
            raise ValidationError("Phone number is required")


        if not display_name or not display_name.strip():
            raise ValidationError('Display_name can not be empty')
      


        phone_number = self.normalize_phone(phone_number)

        user = self.model(
            phone_number = phone_number,
            display_name=display_name,
             **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user




    def create_user(self, phone_number, display_name,  password=None, **extra_fields):
        """
        Create a normal user.
        """
        extra_fields.setdefault('is_admin', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)

    
    
        return self._create_user(
            phone_number=phone_number,
            display_name=display_name,
            password=password,
            **extra_fields)
        


    def create_superuser(self, phone_number, display_name, password=None, **extra_fields):
        """
        Create a superuser with full permissions.
        """
        extra_fields.setdefault('is_admin', True) # for is_staff method
        extra_fields.setdefault('is_superuser', True) # for django permissionMixin
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_admin') is False:
            raise ValidationError("Superuser must have is_admin=True.")

        if extra_fields.get('is_superuser') is False:
                raise ValidationError("Superuser must have is_superuser=True.")



        return self._create_user(
            phone_number=phone_number,
            display_name=display_name,
            password=password,
            **extra_fields
        )

    
    
    
    def normalize_phone(self, phone):

        if phone is None:
            return None
       
        phone = re.sub(r'\D', '', str(phone))

        if len(phone) != 11:
            raise ValidationError("Phone number must have exactly 11 digits")

        return phone




    def active(self):
        return self.get_queryset().filter(is_active=True)
    


    def inactive(self):
        return self.get_queryset().filter(is_active=False)