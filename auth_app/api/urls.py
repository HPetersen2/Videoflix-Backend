from django.urls import path
from .views import RegistrationView, ActivationView, LoginView, LogoutView, TokenRefreshView, PasswordResetView

app_name = 'auth_app'

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('activate/<uidb64>/<token>/', ActivationView.as_view(), name='activate'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('password_reset/', PasswordResetView.as_view(), name='password-reset'),
]