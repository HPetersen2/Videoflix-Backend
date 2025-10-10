from django.db import models
from django.conf import settings

CATEGORY_CHOICES = {
    ("drama", "Drama"),
    ("romance", "Romance"),
}

class Video(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=155)
    description = models.CharField(max_length=255)
    thumbnail = models.ImageField(upload_to=f"thumbnails/")
    category = models.CharField(
        max_length=55, choices=CATEGORY_CHOICES, null=True, blank=True)
    video_file = models.FileField(upload_to=f"videos/")

    def __str__(self):
        return f"{self.title} | Category: {self.category or 'Uncategorized'} | Uploaded: {self.created_at:%Y-%m-%d %H:%M}"
