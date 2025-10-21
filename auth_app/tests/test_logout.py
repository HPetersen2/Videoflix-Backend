import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestLogoutView:
    url = reverse('auth_app:logout')

    def test_logout_blacklist_token(self, django_user_model):
        user = django_user_model.objects.create_user(email="logout@example.com", password="pw1234")
        client = APIClient()
        client.force_authenticate(user=user)
        client.cookies["refresh_token"] = "somevalidtoken"
        response = client.post(self.url)
        assert response.status_code == 200