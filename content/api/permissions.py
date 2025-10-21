from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

class IsAuthenticatedWithCookie(BasePermission):
    """Custom permission to authenticate user via JWT in cookies."""

    def has_permission(self, request, view):
        jwt_authenticator = JWTAuthentication()

        try:
            validated_token = jwt_authenticator.get_validated_token(request.COOKIES.get('access_token'))
            user = jwt_authenticator.get_user(validated_token)

            request.user = user
        
            return user is not None and user.is_authenticated
        
        except (InvalidToken, TokenError):
            return False
        except Exception:
            return False
