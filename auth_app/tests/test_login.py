import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestLoginView:
    url = reverse('auth_app:login')

    def test_login_success(self):
        """Tests successful login and presence of access token in cookies."""
        password = "secret123"
        user = User.objects.create(email="login@example.com", username="login@example.com")
        user.set_password(password)
        user.is_active = True
        user.save()

        client = APIClient()
        response = client.post(self.url, {"email": user.email, "password": password})
        assert response.status_code == 200
        assert "detail" in response.data
        assert response.cookies.get("access_token") is not None

    def test_login_invalid_credentials(self):
        """Tests login failure with invalid email/password combination."""
        client = APIClient()
        response = client.post(self.url, {"email": "nope@example.com", "password": "wrong"})
        assert response.status_code == 400 or response.status_code == 401
