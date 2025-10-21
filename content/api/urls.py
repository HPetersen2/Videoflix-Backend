from django.urls import path
from content.api.views import VideoListView, VideoView, VideoSegmentView

"""
URL patterns for video streaming endpoints:
- /video/ : Lists all available videos.
- /video/<movie_id>/<resolution>/index.m3u8 : HLS playlist for specific movie and resolution.
- /video/<movie_id>/<resolution>/<segment> : Video segment for streaming by movie, resolution, and segment.
"""

urlpatterns = [
    path('video/', VideoListView.as_view(), name='video-list'),
    path('video/<int:movie_id>/<str:resolution>/index.m3u8', VideoView.as_view(), name='video'),
    path('video/<int:movie_id>/<str:resolution>/<str:segment>', VideoSegmentView.as_view(), name='video'),
]
