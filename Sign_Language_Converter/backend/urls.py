from django.urls import path
from .views import upload_media

urlpatterns = [
    path('upload/', upload_media, name='video_upload'),
]