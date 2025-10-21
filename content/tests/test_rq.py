import pytest
from unittest.mock import patch
from content.models import Video
from django.core.files.uploadedfile import SimpleUploadedFile

@pytest.mark.django_db
@patch('content.signals.django_rq.enqueue')
def test_video_post_save_enqueues_convert_video(mock_enqueue):
    video = Video.objects.create(
        title="Test Video",
        description="desc",
        thumbnail=SimpleUploadedFile("thumb.jpg", b"file_content", content_type="image/jpeg"),
        category=None,
        video_file=SimpleUploadedFile("video.mp4", b"file_content", content_type="video/mp4")
    )
    assert mock_enqueue.call_count == 3