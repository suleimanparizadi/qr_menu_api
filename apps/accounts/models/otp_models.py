from django.db import models
from django.utils import timezone
from datetime import timedelta


class OTP(models.Model):

    EXPIRY_MINUTES = 3
    
    
    phone_number = models.CharField(max_length=11, unique=True)
    code = models.IntegerField()
    attempts = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()



    class Meta:
        ordering = ['-created_at']
        verbose_name = 'OTP'
        verbose_name_plural = 'OTPs'
        
        indexes = [
        models.Index(
            fields=['phone_number']
        )
    ]


    def save(self, *args, **kwargs):

        if not self.expired_at:
            self.expired_at = timezone.now() + timedelta(minutes=self.EXPIRY_MINUTES)


        return super().save(*args, **kwargs)


    def is_expired(self):
        return timezone.now() > self.expired_at


    def __str__(self):
        return f"{self.phone_number} - {self.code}"
        