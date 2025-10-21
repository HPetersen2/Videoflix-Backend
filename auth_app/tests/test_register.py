import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()

@pytest.mark.django_db
class TestRegistrationView:
    url = reverse('auth_app:register')

    def test_register_success(self):
        client = APIClient()
        data = {
            "email": "test@example.com",
            "password": "strongpassword",
            "confirmed_password": "strongpassword"
        }
        response = client.post(self.url, data)
        assert response.status_code == 201
        assert "user" in response.data

    def test_register_password_mismatch(self):
        client = APIClient()
        data = {
            "email": "test2@example.com",
            "password": "pw1",
            "confirmed_password": "pw2"
        }
        response = client.post(self.url, data)
        assert response.status_code == 400
        assert "confirmed_password" in response.data


@pytest.mark.django_db
class TestActivationView:
    def test_activation_success(self):
        user = User.objects.create(email="activate@example.com", is_active=False)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        url = reverse('auth_app:activate', kwargs={'uidb64': uid, 'token': token})

        client = APIClient()
        response = client.get(url)
        user.refresh_from_db()
        assert response.status_code == 200
        assert user.is_active

    def test_activation_invalid_token(self):
        user = User.objects.create(email="invalid@example.com", is_active=False)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        url = reverse('auth_app:activate', kwargs={'uidb64': uid, 'token': 'wrongtoken'})

        client = APIClient()
        response = client.get(url)
        user.refresh_from_db()
        assert response.status_code == 400
        assert not user.is_active
