import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestLogoutView:

    def setup_method(self):
        """Initialize APIClient and set logout URL."""
        self.client = APIClient()
        self.url = reverse('auth_app:logout')

    def test_logout_blacklist_token(self):
        """Authenticate user, set refresh token cookie, post logout, expect 200."""
        password = "pw1234"
        user = User.objects.create_user(
            username="logoutuser",
            email="logout@example.com",
            password=password,
            is_active=True
        )
        self.client.force_authenticate(user=user)

        refresh = RefreshToken.for_user(user)

        self.client.cookies['refresh_token'] = str(refresh)

        response = self.client.post(self.url, HTTP_COOKIE=f'refresh_token={str(refresh)}')

        assert response.status_code == 200