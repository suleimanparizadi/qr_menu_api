from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
import re





class UserManager(BaseUserManager):

    def _create_user(self , phone_number, first_name, last_name, email=None,
     password=None,**extra_fields):
     
        if not phone_number:
            raise ValidationError("Phone number is required")
        
        if not first_name:
            raise ValidationError("First name is required")
        
        if not last_name:
            raise ValidationError("Last name is required")


        phone_number = self._normalize_phone(phone_number)
        email = self.normalize_email(email) if email else None

        user = self.model(
            phone_number = phone_number,
            first_name = first_name,
            last_name = last_name,
            email = email,
             **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user




    def create_user(self, phone_number, first_name, last_name, email=None, password=None, **extra_fields):
        """
        Create a normal user.
        """
        extra_fields.setdefault('is_admin', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)

    
    
        return self._create_user(
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            **extra_fields)
        


    def create_superuser(self, phone_number, first_name, last_name, email=None, password=None, **extra_fields):
        """
        Create a superuser with full permissions.
        """
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_admin') is not True:
            raise ValidationError("Superuser must have is_admin=True.")

        if extra_fields.get('is_superuser') is not True:
                raise ValidationError("Superuser must have is_superuser=True.")



        return self._create_user(
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            **extra_fields
        )

    
    
    
    def _normalize_phone(self, phone):

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