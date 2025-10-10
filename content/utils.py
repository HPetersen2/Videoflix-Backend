import subprocess
import os
from rest_framework.response import Response
from django.http import FileResponse
from .models import Video

def convert_video(source, resolution):
    file_directory = os.path.dirname(source)
    file_name = os.path.splitext(os.path.basename(source))
    new_file_name = f"{file_name}_{resolution}p.mp4"
    mp4_dir = os.path.join(file_directory, "mp4")
    os.makedirs(mp4_dir, exist_ok=True)
    new_file_path = os.path.join(mp4_dir, new_file_name)
    
    cmd = f"ffmpeg -i '{source}' -s {resolution} -c:v libx264 -crf 23 -c:a aac -strict -2 '{new_file_path}'"
    subprocess.run(cmd, capture_output=True, shell=True)

    hls_file_name = f"hls_{file_name}_{resolution}p.m3u8"
    hls_directory = os.path.join(file_directory, "hls")
    os.makedirs(hls_directory, exist_ok=True)
    hls_file_path = os.path.join(hls_directory, hls_file_name)
    hls_file_cmd = f"ffmpeg -i '{new_file_path}' -codec copy -start_number 0 -hls_time 10 -hls_list_size 0 -f hls '{hls_file_path}'"
    subprocess.run(hls_file_cmd, capture_output=True, shell=True)

def get_video_file(movie_id, **kwargs):
    resolution = kwargs.get("resolution")
    segment = kwargs.get("segment")

    try:
        video = Video.objects.get(id=movie_id)
        video_path = video.video_file.path
        video_directory = os.path.dirname(video_path)

        hls_file_path = None
        content_type = None

        if resolution:
            content_type = "application/vnd.apple.mpegurl"
            hls_file_path = os.path.join(video_directory, "hls", f"hls_{os.path.splitext(os.path.basename(video_path))[0]}_hd{resolution}.m3u8")

        if segment:
            hls_file_path = os.path.join(video_directory, "hls", segment)
            content_type = "video/MP2T"

        if os.path.exists(hls_file_path):
            return FileResponse(open(hls_file_path, "rb"), content_type=content_type)
        else:
            return Response({"error": "File not found"}, status=404)
        
    except Video.DoesNotExist:
        return Response({"error": "Video not found"}, status=404)