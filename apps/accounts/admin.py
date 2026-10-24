from django.contrib import admin
from apps.accounts.models import otp_models, user_models


admin.site.register(otp_models.OTP)
admin.site.register(user_models.User)
