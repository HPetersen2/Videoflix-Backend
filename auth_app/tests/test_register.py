import pytest
from unittest.mock import patch
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
@patch('auth_app.views.django_rq.get_queue')
def test_registration_view_enqueues_activation_email(mock_get_queue):
    mock_queue = mock_get_queue.return_value
    mock_queue.enqueue.return_value = None

    client = APIClient()
    url = reverse('auth_app:register')
    data = {
        "email": "testuser@example.com",
        "password": "strongpassword123",
        "confirmed_password": "strongpassword123"
    }
    response = client.post(url, data)

    assert response.status_code == 201
    mock_queue.enqueue.assert_called_once_with('auth_app.utils.send_activate_email', 
                                               pytest.anything(), 
                                               pytest.anything())

@pytest.mark.django_db
@patch('auth_app.views.django_rq.get_queue')
def test_password_reset_enqueues_reset_email(mock_get_queue):
    from django.contrib.auth import get_user_model
    User = get_user_model()

    mock_queue = mock_get_queue.return_value
    mock_queue.enqueue.return_value = None

    user = User.objects.create_user(email='reset@test.com', password='pw123456', is_active=True)

    client = APIClient()
    url = reverse('auth_app:password-reset')
    data = {"email": "reset@test.com"}

    response = client.post(url, data)
    assert response.status_code == 200
    mock_queue.enqueue.assert_called_once_with('auth_app.utils.send_reset_password_email', 
                                               user.id, 
                                               pytest.anything())
