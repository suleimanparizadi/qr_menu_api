from rest_framework import views, status, permissions
from rest_framework.response import Response 
from django.contrib.auth import get_user_model
from apps.accounts.api.serializer import auth, profile
from apps.accounts.services.registration import InitiateRegister

User = get_user_model()




class InitiateRegistrationView(views.APIView):

    permission_classes = [permissions.AllowAny]


    def post(self, request):

        serializer = auth.InitiateRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        service = InitiateRegister(data['phone_number'])
        success, message = service.initiate_register(password=data['password'], display_name=data['display_name'])

        if success:
            request.session['user_register_session'] = {
                'display_name' : data['display_name'],
                'password' : data['password']
            }   

            return Response({'message':message}, status=status.HTTP_200_OK)

        return Response({'message':message}, status=status.HTTP_400_BAD_REQUEST)




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

        user, message = InitiateRegister.verify_and_create_user(code, display_name, password)
        request.session.delete()

        return


