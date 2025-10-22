import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestLoginView:
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('auth_app:login')

    def test_login_success(self):
        """Tests successful login and presence of access token in cookies."""
        password = "secret123"
        user = User.objects.create_user(
            username="loginuser",
            email="login@example.com",
            password=password,
            is_active=True
        )

        response = self.client.post(self.url, {
            "email": user.email,
            "password": password
        })

        assert response.status_code == 200
        assert "detail" in response.data
        assert "access_token" in response.cookies, "Access token cookie missing"

    def test_login_invalid_credentials(self):
        """Tests login failure with invalid email/password combination."""
        response = self.client.post(self.url, {
            "email": "nope@example.com",
            "password": "wrong"
        })

        assert response.status_code in [400, 401]
