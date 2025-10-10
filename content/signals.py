from django.dispatch import receiver
from django.db.models.signals import post_save
import django_rq

from content.utils import convert_video
from .models import Video

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    print('Video wurde gespeichert')
    if created:
        print("converting...")
        django_rq.enqueue(convert_video, instance.video_file.path, "hd1080")
        django_rq.enqueue(convert_video, instance.video_file.path, "hd720")
        django_rq.enqueue(convert_video, instance.video_file.path, "hd480")