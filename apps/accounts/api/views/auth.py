from rest_framework import views, status, permissions
from rest_framework.response import Response 
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from apps.accounts.api.serializer import auth, profile
from apps.accounts.services.registration import InitiateRegister, Account, ChangePhone_number
from apps.accounts.services import login



User = get_user_model()




class InitiateRegistrationView(views.APIView):

    permission_classes = [permissions.AllowAny]


    def post(self, request):

        serializer = auth.InitiateRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        service = InitiateRegister(data['phone_number'])
        result = service.initiate_register(password=data['password'], display_name=data['display_name'])

        if result.success:
            request.session['user_register_session'] = {
                'display_name' : data['display_name'],
                'phone_number': data['phone_number'],
                'password' : data['password']
            }   

            return Response({'message':result.message}, status=status.HTTP_200_OK)

        return Response({'message':result.message}, status=status.HTTP_400_BAD_REQUEST)




class VerifyRegisterView(views.APIView):


    permission_classes = [permissions.AllowAny]

    def post(self, request):

        serializer = auth.VerifyLoginOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']
        user_session = request.session.get('user_register_session')
        if not user_session:
            return Response({'message':"unable to find user session. start over!"},
                                                status=status.HTTP_400_BAD_REQUEST)


        password = user_session['password']
        display_name = user_session['display_name']
        phone_number = user_session['phone_number']
        service = InitiateRegister(phone_number=phone_number)
        result = service.verify_and_create_user(code, display_name, password)

        if result.success:

            request.session.delete()
            return Response({'message':result.message, 'token':result.data['token']},
                                        status=status.HTTP_201_CREATED)

        return Response({'message':result.message}, 
                                        status=status.HTTP_400_BAD_REQUEST)




class LoginPasswordView(views.APIView):

    permission_classes = [permissions.AllowAny]


    def post(self, request):

        serializer = auth.PasswordLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = login.PasswordLoginService(
            phone_number=serializer.validated_data['phone_number'],
            password=serializer.validated_data['password']
        )

        result = service.login()

        if result.success:
            return Response({'message':result.message, 'token':result.data['token']},
                                    status=status.HTTP_200_OK)

        return Response({'message':result.message}, status=status.HTTP_400_BAD_REQUEST)





class SendLoginOTP(views.APIView):

    permission_classes = [permissions.AllowAny]


    def post(self, request):

        serializer = auth.SendLoginOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = login.OTPLoginService(serializer.validated_data['phone_number'])

        result = service.send_otp()

        return Response({'message':result.message}, status=status.HTTP_200_OK 
                        if result.success else status.HTTP_400_BAD_REQUEST)



class VerifyOTPLogin(views.APIView):

    """
        Verifies OTP login/registration codes.
    
        phone_number is required here because the frontend resends it
        from state (stored during the "send OTP" step). The user does
        not re-enter it. This keeps the backend stateless.
    """


    permission_classes = [permissions.AllowAny]


    def post(self, request):

        serializer = auth.VerifyLoginOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
    
        service = login.OTPLoginService(serializer.validated_data['phone_number'])

        result =  service.verify_otp(serializer.validated_data['code'])

        if result.success:
            return Response({'message':result.message, 'token':result.data['token']},
                                    status=status.HTTP_200_OK)

        return Response({'message':result.message}, status=status.HTTP_400_BAD_REQUEST)




class LogOutView(views.APIView):


    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        service = Account(request.user)

        result = service.logout()

        return Response({'message':result.message}, status=status.HTTP_200_OK)




class ProfileView(views.APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        user = request.user 
        serializer = auth.UserSerializer(user)

        return Response({'data':serializer.data}, status=status.HTTP_200_OK)


class ChangeDisplayName(views.APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):

        serializer = auth.ChangeDisplayNameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        display_name = serializer.validated_data['display_name']

        service = Account(request.user)
        result = service.changing_display_name(display_name)

        return Response({'message':result.message}, status=status.HTTP_200_OK)


        
class ChangePhoneNumberSendOTPView(views.APIView):

    permission_classes = [permissions.IsAuthenticated]


    def post(self, request):


        serializer = auth.ChangePhoneNumberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_phone_number = serializer.validated_data['new_phone_number']

        service = ChangePhone_number(user=request.user, phone_number=new_phone_number)
        
        result = service.send_otp()

        return Response({'message':result.message},
                         status=status.HTTP_200_OK if result.success else status.HTTP_400_BAD_REQUEST)



class ChangePhoneNumberVerifyOTPView(views.APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):

        serializer = auth.VerifyLoginOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data['code']
        phone_number = serializer.validated_data['phone_number']
        service = ChangePhone_number(phone_number=phone_number, user=request.user)

        result = service.Verify_otp(code)

        if result.success:
            return Response({'message':result.message, 'new_phone_number':result.data['phone_number']},
                                        status=status.HTTPresult.message_200_OK)

        return Response({'message':result.message}, status=status.HTTP_400_BAD_REQUEST)


    
        

