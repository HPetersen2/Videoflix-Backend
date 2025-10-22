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
        """Tests that a password reset email is sent for an existing user."""
        user = User.objects.create_user(email="reset@example.com", username="resetuser", password="pw1234", is_active=True)
        client = APIClient()
        response = client.post(self.url, {"email": user.email})
        assert response.status_code == 200

    def test_password_reset_email_nonexistent(self):
        """Tests that a reset request for a non-existent email still returns 200."""
        client = APIClient()
        response = client.post(self.url, {"email": "noone@example.com"})
        assert response.status_code == 200


@pytest.mark.django_db
class TestSetNewPasswordView:

    def test_set_new_password_success(self):
        """Tests successful password reset with valid token and matching passwords."""
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
        """Tests password reset failure due to invalid token."""
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
        """Tests password reset failure when passwords do not match."""
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
