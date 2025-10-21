from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.contrib.auth import get_user_model
import django_rq
from auth_app.utils import send_activate_email, send_reset_password_email
from .serializers import RegistrationSerializer, CustomTokenObtainPairSerializer, PasswordResetSerializer, SetNewPasswordSerializer

User = get_user_model()

class RegistrationView(APIView):
    """Registers a new user and sends an activation email."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        data = {}
        if serializer.is_valid():
            saved_account = serializer.save()

            uid = urlsafe_base64_encode(force_bytes(saved_account.pk))
            token = default_token_generator.make_token(saved_account)

            activation_path = reverse('auth_app:activate', kwargs={'uidb64': uid, 'token': token})

            activation_link = f'http://127.0.0.1:5500/pages/auth/activate.html?uid={uid}&token={token}'

            django_rq.get_queue('default').enqueue('auth_app.utils.send_activate_email', saved_account, activation_link)

            data = {
                "user": {
                    "id": saved_account.pk,
                    "email": saved_account.email
                },
                "token": "activation_token"
            }
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivationView(APIView):
    """Activates a user account via token from the activation email."""
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({"message": "Invalid activation link."}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"message": "Account successfully activated."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    """Logs in a user and returns tokens as cookies."""
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        """Obtain JWT tokens and set them as cookies."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.user
        tokens = serializer.validated_data

        access = tokens.get("access")
        refresh = tokens.get("refresh")

        response = Response({
            "detail": "Login successful",
            "user": {
                "id": user.id,
                "username": user.username
            }
        })

        if access and refresh:
            response.set_cookie(
                key="access_token",
                value=str(access),
                httponly=True,
                secure=True,
                samesite="None"
            )

            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                httponly=True,
                secure=True,
                samesite="None"
            )

        return response


class LogoutView(APIView):
    """Logs out the user and blacklists the refresh token."""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Blacklist the refresh token and log the user out."""
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token is None:
            response = Response({"detail": "No refresh token cookie provided."}, status=status.HTTP_200_OK)
        else:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError as e:
                return Response({"detail": "Invalid or expired refresh token."}, status=status.HTTP_400_BAD_REQUEST)

            response = Response({"detail": "Logout successful! All tokens will be deleted. Refresh token is now invalid."}, status=status.HTTP_200_OK)

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response


class TokenRefreshView(TokenRefreshView):
    """Refreshes JWT access token using the refresh token stored in cookies."""

    def post(self, request, *args, **kwargs):
        """Refresh the access token using the refresh token stored in cookies."""
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token is None:
            return Response(
                {"detail": "Refresh token not found!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data={"refresh": refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except:
            return Response(
                {"detail": "Refresh token invalid!"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        access_token = serializer.validated_data.get("access")

        response = Response({"detail": "Token refreshed", "access": "new_access_token"})
        response.set_cookie(
            key="access_token",
            value=str(access_token),
            httponly=True,
            secure=False,
            samesite="None"
        )

        return response


class PasswordResetView(APIView):
    """Sends a password reset link to the user's email if account exists."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data.get('email')

        try:
            user = User.objects.get(email=email)
            if user.is_active:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)

                verification_link = f'http://127.0.0.1:5500/pages/auth/confirm_password.html?uid={uid}&token={token}'

                django_rq.get_queue('default').enqueue(
                    'auth_app.utils.send_reset_password_email',
                    user.id,
                    verification_link
                )
        except User.DoesNotExist:
            pass

        return Response({"detail": "If an account with this email exists, a password reset link has been sent."}, status=status.HTTP_200_OK)


class SetNewPasswordView(APIView):
    """Resets the user's password using a valid token and uid."""
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        serializer = SetNewPasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({"detail": "Invalid link."}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({"detail": "Your password has been successfully reset."}, status=status.HTTP_200_OK)
