from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.core.mail import send_mail
from .serializers import RegistrationSerializer
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        data = {}
        if serializer.is_valid():
            saved_account = serializer.save()

            uid = urlsafe_base64_encode(force_bytes(saved_account.pk))
            token = default_token_generator.make_token(saved_account)


            activation_path = reverse('auth_app:activate', kwargs={
                                      'uidb64': uid, 'token': token})
            activation_link = request.build_absolute_uri(activation_path)

            # render email (text fallback + html)
            subject = 'Activate your account'
            from_email = None  # uses DEFAULT_FROM_EMAIL
            context = {
                'user': saved_account,
                'activation_link': activation_link,
            }
            text_content = render_to_string(
                'activation_email.txt', context)
            html_content = render_to_string(
                'activation_email.html', context)

            email = EmailMultiAlternatives(
                subject, text_content, from_email, ['petermann2@web.de']) #saved_account.email
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)

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
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({"detail": "Invalid activation link"}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"detail": "Account activated"}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
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
                samesite="Lax"
            )

            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                httponly=True,
                secure=True,
                samesite="Lax"
            )

        return response