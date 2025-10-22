import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestTokenRefreshView:
    url = reverse('auth_app:token-refresh')

    def test_refresh_token_success(self):
        """Create user, set refresh token cookie, post refresh, expect access token in response."""
        user = User.objects.create_user(email="refresh@example.com", username="refreshuser", password="pw1234", is_active=True)
        refresh = RefreshToken.for_user(user)
        refresh_token = str(refresh)

        client = APIClient()
        client.cookies['refresh_token'] = refresh_token

        response = client.post(self.url)
        assert response.status_code == 200
        assert "access_token" in response.data or "access_token" in response.cookies

