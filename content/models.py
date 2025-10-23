from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

def validate_thumbnail_format(image):
    """Custom validator to allow only PNG and JPEG files."""
    valid_mime_types = ['image/jpeg', 'image/png']
    if image.file.content_type not in valid_mime_types:
        raise ValidationError('Nur PNG- und JPEG-Bilder sind erlaubt.')
    
def validate_video_format(video):
    """Custom validator to allow only common video formats."""
    valid_mime_types = [
        'video/mp4',
        'video/quicktime',
        'video/x-msvideo',
        'video/x-matroska',
        'video/webm',
    ]
    if hasattr(video, 'file') and video.file.content_type not in valid_mime_types:
        raise ValidationError('Nur MP4, MOV, AVI, MKV oder WEBM-Videos sind erlaubt.')

CATEGORY_CHOICES = {
    ("drama", "Drama"),
    ("romance", "Romance"),
}

class Video(models.Model):
    """Represents a video with metadata, file, and thumbnail."""
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=155)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to=f"thumbnails/", null=False, blank=False,
            validators=[
            FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg']),
            validate_thumbnail_format
        ])
    category = models.CharField(
        max_length=55, choices=CATEGORY_CHOICES)
    video_file = models.FileField(
        upload_to="videos/",
        null=False,
        blank=False,
        validators=[
            FileExtensionValidator(allowed_extensions=['mp4', 'mov', 'avi', 'mkv', 'webm']),
            validate_video_format,
        ],
    )

    def __str__(self):
        return f"{self.title} | Category: {self.category or 'Uncategorized'} | Uploaded: {self.created_at:%Y-%m-%d %H:%M}"
