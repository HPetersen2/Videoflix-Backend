import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.tokens import default_token_generator

@pytest.mark.django_db
class TestTokenRefreshView:
    url = reverse('auth_app:token-refresh')

    def test_refresh_token_success(self):
        pass

    def test_refresh_token_missing_cookie(self):
        client = APIClient()
        response = client.post(self.url)
        assert response.status_code == 400