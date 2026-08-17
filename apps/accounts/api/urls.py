from django.urls import path
from apps.accounts.api.views import auth




app_name = 'accounts'

urlpatterns = [

    path('register/', auth.InitiateRegistrationView.as_view(), name='initiate_register'),
    path('verify/', auth.VerifyRegisterView.as_view(), name='verify_register'),
    path('login/password/', auth.LoginPasswordView.as_view(), name='login_password'),
    path('login/send_otp/', auth.SendLoginOTP.as_view(), name='login_send_otp'),
    path('login/verify/', auth.VerifyOTPLogin.as_view(), name='login_verify'),
    path('logout/', auth.LogOutView.as_view(), name='logout'),
    path('profile/', auth.ProfileView.as_view(), name='profile'),
    path('change/phone/send_otp/', auth.ChangePhoneNumberSendOTPView.as_view(), name='change_phone_send_otp'),
    path('change/phone/verify_otp/', auth.ChangePhoneNumberVerifyOTPView.as_view(), name='change_phone_verify_otp'),
    path('change/name/', auth.ChangeDisplayName.as_view(), name='change_name'),
    
    
]
