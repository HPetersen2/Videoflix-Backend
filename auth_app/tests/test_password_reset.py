import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()

@pytest.mark.django_db
class TestPasswordResetView:
    url = reverse('auth_app:password-reset')

    def test_password_reset_email_sent(self):
        user = User.objects.create(email="reset@example.com", is_active=True)
        client = APIClient()
        response = client.post(self.url, {"email": user.email})
        assert response.status_code == 200

    def test_password_reset_email_nonexistent(self):
        client = APIClient()
        response = client.post(self.url, {"email": "noone@example.com"})
        assert response.status_code == 200


@pytest.mark.django_db
class TestSetNewPasswordView:
    def test_set_new_password_success(self):
        user = User.objects.create(email="setpass@example.com", is_active=True)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        url = reverse('auth_app:set-new-password', kwargs={'uidb64': uid, 'token': token})

        client = APIClient()
        data = {
            "new_password": "newstrongpass",
            "confirm_password": "newstrongpass"
        }
        response = client.post(url, data)
        user.refresh_from_db()
        assert response.status_code == 200

    def test_set_new_password_invalid_token(self):
        user = User.objects.create(email="setfail@example.com", is_active=True)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        url = reverse('auth_app:set-new-password', kwargs={'uidb64': uid, 'token': 'badtoken'})

        client = APIClient()
        data = {
            "new_password": "newpass",
            "confirm_password": "newpass"
        }
        response = client.post(url, data)
        assert response.status_code == 400

    def test_set_new_password_mismatch(self):
        user = User.objects.create(email="setmismatch@example.com", is_active=True)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        url = reverse('auth_app:set-new-password', kwargs={'uidb64': uid, 'token': token})

        client = APIClient()
        data = {
            "new_password": "pass1",
            "confirm_password": "pass2"
        }
        response = client.post(url, data)
        assert response.status_code == 400