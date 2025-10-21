from rest_framework import generics
from rest_framework.views import APIView
from content.models import Video
from content.utils import get_video_file
from .permissions import IsAuthenticatedWithCookie
from .serializers import VideoListSerializer

class VideoListView(generics.ListAPIView):
    """Returns a list of all videos with authentication via cookie."""
    permission_classes = [IsAuthenticatedWithCookie]
    queryset = Video.objects.all()
    serializer_class = VideoListSerializer


class VideoView(APIView):
    """Streams a specific video file by ID and resolution."""
    permission_classes = [IsAuthenticatedWithCookie]

    def get(self, request, *args, **kwargs):
        movie_id = kwargs.get("movie_id")
        resolution = kwargs.get("resolution")

        return get_video_file(movie_id, resolution=resolution)


class VideoSegmentView(APIView):
    """Streams a specific video segment by ID and segment number."""
    permission_classes = [IsAuthenticatedWithCookie]

    def get(self, request, *args, **kwargs):
        movie_id = kwargs.get("movie_id")
        segment = kwargs.get("segment")

        return get_video_file(movie_id, segment=segment)
