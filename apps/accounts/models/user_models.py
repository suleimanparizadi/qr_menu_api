from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from apps.accounts.models.manager import UserManager
import uuid



class User(AbstractBaseUser, PermissionsMixin):



    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )


    phone_number = models.CharField(max_length=11, unique=True, 
    validators=[
        RegexValidator(
        regex=r'^09\d{9}$',
        message='Phone number must be in this format: 09xxxxxxxxx'
            )
        ]
    )


    username = models.CharField(max_length=125)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    date_of_birth = models.DateField(null=True, blank=True)

    last_login_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)   

    terms_accepted = models.BooleanField(default=False)
    terms_accepted_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()


    class Meta:

        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

        indexes = [
            models.Index(fields=['created_at'], name='created_at_idx'),
            models.Index(fields=['is_active'], name='is_active_idx'),
        ]

        app_label = 'accounts'  



    def __str__(self):
        return f"{self.phone_number}-{self.username}"

    
    @property
    def is_staff(self):
        return self.is_admin


    def deactivate(self):
        if self.is_active:
            self.is_active = False
            self.save(update_fields=['is_active', 'updated_at'])

        return None




    def activate(self):
        if not self.is_active:
            self.is_active = True
            self.save(update_fields=['is_active', 'updated_at'])

        return None
