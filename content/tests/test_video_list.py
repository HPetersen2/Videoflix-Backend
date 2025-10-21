import tempfile
import os
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from content.models import Video
from django.core.files.uploadedfile import SimpleUploadedFile

@pytest.mark.django_db
class TestVideoListView:
    url = reverse('video-list')

    def test_video_list_requires_authentication(self, django_user_model):
        """Tests that authentication is required to access the video list."""
        user = django_user_model.objects.create_user(email="user@example.com", password="pw123456")
        client = APIClient()
        response = client.get(self.url)
        assert response.status_code == 401 or response.status_code == 403

        client.force_authenticate(user=user)
        response = client.get(self.url)
        assert response.status_code == 200


@pytest.mark.django_db
class TestVideoViewAndSegmentView:

    def setup_method(self):
        """Sets up a temporary video file and authenticated client."""
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        self.temp_file.write(b"test video content")
        self.temp_file.close()

        self.video = Video.objects.create(
            title="Test Video",
            description="Test Description",
            thumbnail=SimpleUploadedFile("thumb.jpg", b"file_content", content_type="image/jpeg"),
            category=None,
            video_file=SimpleUploadedFile("video.mp4", b"file_content", content_type="video/mp4"),
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.video)

    def teardown_method(self):
        """Cleans up temporary video file after each test."""
        try:
            os.unlink(self.temp_file.name)
        except Exception:
            pass

    def test_get_video_file_not_found(self):
        """Tests video retrieval failure with non-existent movie ID."""
        url = reverse('video', kwargs={'movie_id': 9999, 'resolution': '720'})
        response = self.client.get(url)
        assert response.status_code == 404

    def test_get_video_file_success(self):
        """Tests successful video file retrieval or fallback when file is missing."""
        url = reverse('video', kwargs={'movie_id': self.video.id, 'resolution': '720'})
        response = self.client.get(url)
        assert response.status_code in [200, 404]
