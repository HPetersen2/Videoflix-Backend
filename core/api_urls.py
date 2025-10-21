from django.urls import path, include

"""
Root URL patterns including:
- Authentication-related API routes from auth_app.
- Content-related API routes from content app.
Both are included at the root URL namespace.
"""

urlpatterns = [
    path('', include('auth_app.api.urls')),
    path('', include('content.api.urls')),
]
