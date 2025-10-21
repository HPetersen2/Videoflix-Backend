import django_rq
import os
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from content.utils import convert_video
from .models import Video

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """Triggers video conversion tasks after a new video is saved."""
    print('Video saved')
    if created:
        print("converting...")
        django_rq.enqueue(convert_video, instance.video_file.path, "hd1080")
        django_rq.enqueue(convert_video, instance.video_file.path, "hd720")
        django_rq.enqueue(convert_video, instance.video_file.path, "hd480")


@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):
    """Cleans up original and converted video files after deletion."""
    if instance.thumbnail and os.path.isfile(instance.thumbnail.path):
        thumbnail_path = instance.thumbnail.path

        os.remove(thumbnail_path)

    if instance.video_file and os.path.isfile(instance.video_file.path):
        video_path = instance.video_file.path
        video_directory = os.path.dirname(video_path)
        video_filename_base = os.path.splitext(os.path.basename(video_path))[0]

        os.remove(video_path)

        search_suffix = ['hls', 'mp4']

        for suffix in search_suffix:
            dir = os.path.join(video_directory, suffix)
            if os.path.isdir(dir):
                for root, _, files in os.walk(dir):
                    for file in files:
                        if video_filename_base in file:
                            file_path_to_delete = os.path.join(root, file)
                            if os.path.isfile(file_path_to_delete):
                                os.remove(file_path_to_delete)
