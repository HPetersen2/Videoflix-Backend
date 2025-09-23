from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.core.signing import dumps, loads, BadSignature, SignatureExpired
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .serializers import RegistrationSerializer



class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        data = {}
        if serializer.is_valid():
            # Erzeuge einen signierten Token mit den validierten Daten (inkl. Passwort)
            token = dumps(serializer.validated_data, salt="registration")

            # Erzeuge Link zur Aktivierung (SITE_URL muss in settings gesetzt sein)
            activation_path = reverse("auth_app:activate")  # siehe urls unten
            activation_link = f"{settings.SITE_URL}{activation_path}?token={token}"

            subject = "Dein Aktivierungslink"
            message = f"Bitte aktiviere dein Konto mit folgendem Link:\n\n{activation_link}\n\nDer Link läuft in 24 Stunden ab."
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
            recipient_list = [serializer.validated_data.get("email")]

            # Sende Mail (Email-Backend in settings konfigurieren)
            send_mail(subject, message, from_email,
                      recipient_list, fail_silently=False)

            return Response({"detail": "Aktivierungslink wurde per E-Mail gesendet."}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.GET.get("token")
        if not token:
            return Response({"detail": "Token fehlt."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # max_age in Sekunden (hier 24h)
            data = loads(token, salt="registration", max_age=24 * 3600)
        except SignatureExpired:
            return Response({"detail": "Token abgelaufen."}, status=status.HTTP_400_BAD_REQUEST)
        except BadSignature:
            return Response({"detail": "Ungültiger Token."}, status=status.HTTP_400_BAD_REQUEST)

        # Erstelle den User jetzt endgültig
        serializer = RegistrationSerializer(data=data)
        if serializer.is_valid():
            saved_account = serializer.save()
            response_data = {
                "user": {
                    "id": saved_account.pk,
                    "email": saved_account.email,
                }
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
