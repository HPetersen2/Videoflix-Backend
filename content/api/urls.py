from django.urls import path
from content.api.views import VideoListView

urlpatterns = [
    path('video/', VideoListView.as_view(), name='video-list'),
    path('video/<int:movie_id>/<str:resolution>/index.m3u8/', name='video')
]