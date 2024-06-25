from django.http import JsonResponse
from rest_framework.decorators import api_view
from .media_processing import convert_image_to_text, convert_video_to_text
import os

# Upload directory
UPLOAD_DIR = 'media/uploads/'

# Handle POST request by frontend and return the annotations
@api_view(['POST'])
def upload_media(request):

    # Check if media is present
    if 'media' not in request.FILES:
        return JsonResponse({'error': 'No media file provided.'}, status=400)

    # Define media file with file extension and filename
    media_file = request.FILES['media']
    file_extension = os.path.splitext(media_file.name)[1].lower()
    file_name = os.path.splitext(media_file.name)[0]

    # Create the upload path for the media file
    upload_path = os.path.join(UPLOAD_DIR, media_file.name)

    try:
        # Ensure the upload and processed directories exist
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # Save the uploaded file to UPLOAD_DIR
        with open(upload_path, 'wb') as f:
            for chunk in media_file.chunks():
                f.write(chunk)

        # Process media file according to thier type
        if file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
            detected_text, annotations = convert_image_to_text(upload_path)
            media_type = 'image'
        elif file_extension in ['.mp4', '.avi', '.mov', '.mkv']:
            detected_text, annotations = convert_video_to_text(upload_path)
            media_type = 'video'
        else:
            return JsonResponse({'error': 'Unsupported file type.'})

        # Delete the file after processing is done
        if os.path.exists(upload_path):
            os.remove(upload_path)

        # Return our annotations if everything goes correctly
        return JsonResponse({'message': 'Media processed successfully.', 'text': detected_text, 'annotations': annotations, 'media_type': media_type})

    except Exception as e:
        # If any error occurs, delete the file if it was saved
        if os.path.exists(upload_path):
            os.remove(upload_path)
        # Return error
        return JsonResponse({'error': str(e)}, status=500)