from django.urls import path
from content.api.views import VideoListView, VideoView, VideoSegmentView

urlpatterns = [
    path('video/', VideoListView.as_view(), name='video-list'),
    path('video/<int:movie_id>/<str:resolution>/index.m3u8', VideoView.as_view(), name='video'),
    path('video/<int:movie_id>/<str:resolution>/<str:segment>', VideoSegmentView.as_view(), name='video'),
]