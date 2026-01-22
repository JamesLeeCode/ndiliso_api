from django.http import JsonResponse
from .models import Funeral, Dependent, User, Village
from .serializers import  DependentSerializer, FuneralSerializer, UserSerializer, VillageSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
import jwt, datetime
from .authentication import authenticate_request
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives




@api_view(['GET', 'POST']) 
def village_list(request):
   
    if request.method == 'GET':
        villages = Village.objects.all()
        serializer = VillageSerializer(villages, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = VillageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET', 'POST'])
def funeral_list(request):
    user = authenticate_request(request)

    if request.method == 'GET':
        funerals = Funeral.objects.filter(user=user)
        serializer = FuneralSerializer(funerals, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = FuneralSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)  # 🔑 attach user
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)



@api_view(['GET', 'POST'])
def dependent_list(request):
    user = authenticate_request(request)

    if request.method == 'GET':
        dependents = Dependent.objects.filter(user=user)
        serializer = DependentSerializer(dependents, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = DependentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)  # 🔑 attach user
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
def funeral_detail(request, id):
    user = authenticate_request(request)

    try:
        funeral = Funeral.objects.get(id=id, user=user)
    except Funeral.DoesNotExist:
        return Response({'message': 'Funeral not found'}, status=404)

    if request.method == 'GET':
        serializer = FuneralSerializer(funeral)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = FuneralSerializer(funeral, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.errors, status=400)

    if request.method == 'DELETE':
        funeral.delete()
        return Response(status=204)
    
    
@api_view(['GET', 'PUT', 'DELETE'])
def dependent_detail(request, id):
    user = authenticate_request(request)

    try:
        dependent = Dependent.objects.get(id=id, user=user)
    except Dependent.DoesNotExist:
        return Response({'message': 'Dependent not found'}, status=404)

    if request.method == 'GET':
        serializer = DependentSerializer(dependent)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = DependentSerializer(dependent, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    if request.method == 'DELETE':
        dependent.delete()
        return Response(status=204)

    
class UserView(APIView):
    def get(self, request):
        user = authenticate_request(request)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')

        return Response({
            'access_token': token,
            'token_type': 'Bearer'
        })


class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()

        # Always return the same response (security best practice)
        if not user:
            return Response(
                {'message': 'If this email exists, a reset link was sent'},
                status=status.HTTP_200_OK
            )

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        reset_link = f"https://yourapp.com/reset-password?token={token}"

        subject = "Reset Your Password 🔐"
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [email]

        text_content = f"""
        You requested a password reset.

        Click the link below to reset your password:
        {reset_link}

        If you did not request this, please ignore this email.
        """

        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f3f4f6; padding: 20px;">
                <div style="max-width: 600px; margin: auto; background: #ffffff;
                            padding: 24px; border-radius: 10px;">

                    <h2 style="color: #111827;">Password Reset</h2>

                    <p style="font-size: 16px; color: #374151;">
                        We received a request to reset your password.
                    </p>

                    <p style="font-size: 16px; color: #374151;">
                        Click the button below to set a new password. This link
                        will expire in 15 minutes.
                    </p>

                    <a href="{reset_link}"
                       style="display: inline-block; margin-top: 20px;
                              padding: 14px 24px; background-color: #dc2626;
                              color: #ffffff; text-decoration: none;
                              border-radius: 8px; font-weight: bold;">
                        Reset Password
                    </a>

                    <hr style="margin: 30px 0;">

                    <p style="font-size: 12px; color: #9ca3af;">
                        If you didn’t request a password reset, you can safely ignore this email.
                    </p>
                </div>
            </body>
        </html>
        """

        email_message = EmailMultiAlternatives(
            subject,
            text_content,
            from_email,
            to
        )
        email_message.attach_alternative(html_content, "text/html")
        email_message.send()

        return Response(
            {'message': 'If this email exists, a reset link was sent'},
            status=status.HTTP_200_OK
        )  



class PasswordResetConfirmView(APIView):
    def post(self, request):
        token = request.data.get('token')
        new_password = request.data.get('password')

        if not token or not new_password:
            return Response(
                {'error': 'Token and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Reset token expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')

        user = User.objects.filter(id=payload['id']).first()

        if not user:
            raise AuthenticationFailed('User not found')

        user.set_password(new_password)
        user.save()

        return Response({'message': 'Password reset successful'})
