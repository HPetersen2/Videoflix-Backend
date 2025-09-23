from django.dispatch import receiver
from django.db.models import post_save

from content.tasks import convert_480p
from .models import Video

# @receiver(post_save, sender=Video)
# def video_post_save(sender, instance, created, **kwargs):
#     print('Video wurde gespeichert')
#     if created:
#         convert_480p(instance.video_file.path)