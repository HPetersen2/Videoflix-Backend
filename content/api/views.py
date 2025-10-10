from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from content.models import Video
from .serializers import VideoListSerializer

class VideoListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Video.objects.all()
    serializer_class = VideoListSerializer