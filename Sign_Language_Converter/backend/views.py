from django.http import JsonResponse
from rest_framework.decorators import api_view
from .media_processing import convert_image_to_text, convert_video_to_text
import os

UPLOAD_DIR = 'media/uploads/'

# Handle POST request by frontend and return the annotations and delete the media after this
@api_view(['POST'])
def upload_media(request):

    if 'media' not in request.FILES:
        return JsonResponse({'error': 'No media file provided.'}, status=400)

    media_file = request.FILES['media']
    file_extension = os.path.splitext(media_file.name)[1].lower()

    upload_path = os.path.join(UPLOAD_DIR, media_file.name)

    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        with open(upload_path, 'wb') as f:
            for chunk in media_file.chunks():
                f.write(chunk)

        if file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
            detected_text, annotations = convert_image_to_text(upload_path)
            media_type = 'image'
        elif file_extension in ['.mp4', '.avi', '.mov', '.mkv']:
            detected_text, annotations = convert_video_to_text(upload_path)
            media_type = 'video'
        else:
            return JsonResponse({'error': 'Unsupported file type.'})

        if os.path.exists(upload_path):
            os.remove(upload_path)

        return JsonResponse({'message': 'Media processed successfully.', 'text': detected_text, 'annotations': annotations, 'media_type': media_type})

    except Exception as e:
        if os.path.exists(upload_path):
            os.remove(upload_path)
        return JsonResponse({'error': str(e)}, status=500)