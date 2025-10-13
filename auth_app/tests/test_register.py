import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def user():
    """Fixture to create a test user."""
    return User.objects.create_user(
        email='test@test.de',
        password='testpassword'
    )


@pytest.fixture
def register_url():
    """Fixture to provide the registration URL."""
    return reverse('register')  # ensure you have this URL name in urls.py


@pytest.fixture
def api_client():
    """Fixture to return an instance of APIClient."""
    return APIClient()


@pytest.mark.django_db
def test_register(api_client, register_url):
    """Test registering a new user."""
    user_data = {
        "email": "newuser@test.de",
        "password": "testpassword",
        "confirmed_password": "testpassword"
    }

    response = api_client.post(register_url, user_data, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(email="newuser@test.de").exists()

    response_data = response.json()
    assert "user" in response_data
    assert response_data["user"]["email"] == "newuser@test.de"
    assert "token" in response_data
    assert response_data["token"] == "activation_token"


@pytest.mark.django_db
def test_register_existing_email(api_client, register_url, user):
    """Test registering with an email that already exists."""
    data = {
        "email": "test@test.de",
        "password": "testpassword",
        "confirmed_password": "testpassword"
    }

    response = api_client.post(register_url, data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'email' in response.json()


@pytest.mark.django_db
def test_register_invalid_email(api_client, register_url):
    """Test registering with an invalid email format."""
    data = {
        "email": "invalid-email-format",
        "password": "securepassword",
        "confirmed_password": "securepassword"
    }

    response = api_client.post(register_url, data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'email' in response.json()


@pytest.mark.django_db
def test_register_missing_fields(api_client, register_url):
    """Test registering with missing or empty fields."""
    data = {
        "email": "test@test.de",
        "password": ""
    }

    response = api_client.post(register_url, data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'password' in response.json()


@pytest.mark.django_db
def test_register_password_mismatch(api_client, register_url):
    """Test registering with mismatching password and confirmed_password."""
    data = {
        "email": "another@test.de",
        "password": "password123",
        "confirmed_password": "differentpassword"
    }

    response = api_client.post(register_url, data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'non_field_errors' in response.json() or 'confirmed_password' in response.json()