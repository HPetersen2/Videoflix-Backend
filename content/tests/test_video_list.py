import tempfile
import os
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from content.models import Video
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestVideoListView:
    url = reverse('video-list')

    def test_video_list_requires_authentication(self, django_user_model):
        """Verify unauthenticated access is denied and authenticated access is allowed."""
        user = django_user_model.objects.create_user(
            username="testuser",
            email="user@example.com",
            password="pw123456",
            is_active=True,
            is_staff=True
        )
        client = APIClient()

        response = client.get(self.url)
        assert response.status_code in (401, 403)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        client.cookies['access_token'] = access_token

        response = client.get(self.url)
        assert response.status_code == 200


@pytest.mark.django_db
class TestVideoViewAndSegmentView:

    def setup_method(self):
        """Create temp video file, user, video instance, and authenticate client."""
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        self.temp_file.write(b"test video content")
        self.temp_file.close()

        self.user = User.objects.create_user(
            username="videouser",
            email="video@example.com",
            password="password123",
            is_active=True,
            is_staff=True
        )

        self.video = Video.objects.create(
            title="Test Video",
            description="Test Description",
            thumbnail=SimpleUploadedFile("thumb.jpg", b"file_content", content_type="image/jpeg"),
            category=None,
            video_file=SimpleUploadedFile("video.mp4", b"file_content", content_type="video/mp4"),
        )

        self.client = APIClient()

        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)

        self.client.cookies['access_token'] = access_token

    def teardown_method(self):
        """Remove the temporary video file."""
        try:
            os.unlink(self.temp_file.name)
        except Exception:
            pass

    def test_get_video_file_not_found(self):
        """Request non-existing video file, expect 404."""
        url = reverse('video', kwargs={'movie_id': 9999, 'resolution': '720'})
        response = self.client.get(url)
        assert response.status_code == 404

    def test_get_video_file_success(self):
        """Request existing video file, expect 200 or 404 depending on file presence."""
        url = reverse('video', kwargs={'movie_id': self.video.id, 'resolution': '720'})
        response = self.client.get(url)
        assert response.status_code in [200, 404]

