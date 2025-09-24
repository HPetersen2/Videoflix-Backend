from django.urls import path
from .views import RegistrationView, ActivationView

app_name = 'auth_app'

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('activate/<uidb64>/<token>/', ActivationView.as_view(), name='activate')
]