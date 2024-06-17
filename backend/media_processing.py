import cv2
from roboflow import Roboflow
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
api_key = os.getenv('ROBOFLOW_API_KEY')

# Initialize Roboflow object with your API key
rf = Roboflow(api_key=api_key)

# Access the project and specific version
workspace_name = "learn-ub3rr"
project_name = "american-sign-language-letters-aydom"
version_number = 1

project = rf.workspace(workspace_name).project(project_name)
version = project.version(version_number)

# Load the model from the version
model = version.model

# Process Image
def convert_image_to_text(image_path):
    try:
        # Read the image
        image = cv2.imread(image_path)

        # Check if the image is loaded correctly
        if image is None:
            return "Could not load image... Image not found..."

        # Set the target width and height
        target_width, target_height = 832, 832

        # Resize the image to the target width and height
        resized_image = cv2.resize(image, (target_width, target_height))

        # Perform object detection on the resized image
        results = model.predict(resized_image, confidence=15, overlap=5).json()

        # Define predicted label list
        pred_label_list = []

        # Collect predictions
        if 'predictions' in results:
            for prediction in results['predictions']:
                class_label = prediction['class']
                pred_label_list.append(class_label)

        # Release everything
        cv2.destroyAllWindows()

        # Return the predicted labels as a concatenated string
        return ' '.join(pred_label_list)
    except Exception as e:
        return f"Error processing image: {str(e)}"

# Process Video
def convert_video_to_text(video_path):
    try:
        # Open the video file
        cap = cv2.VideoCapture(video_path)

        # Check if the video file is opened correctly
        if not cap.isOpened():
            return "Error: Could not open video file."

        # Get total number of frames in the video
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_skip = 10  # Process every 10th frame

        # Text storage for unique detections
        unique_text = set()

        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()

            if not ret:
                break

            # Skip frames
            current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            if current_frame % frame_skip != 0:
                continue

            # Resize frame to match model input size
            frame_resized = cv2.resize(frame, (832, 832))

            # Perform object detection on the resized frame
            results = model.predict(frame_resized, confidence=15, overlap=5).json()

            # Process detections and collect text
            current_text = ""
            if 'predictions' in results:
                for prediction in results['predictions']:
                    class_label = prediction['class']
                    current_text += class_label

            # Add unique text to set
            unique_text.add(current_text)

            # Print progress
            progress = (current_frame / total_frames) * 100
            print(f"Processing frame {current_frame}/{total_frames} ({progress:.2f}%)")

        # Release everything when done
        cap.release()
        cv2.destroyAllWindows()

        # Return unique text found in the video
        return ''.join(unique_text)
    except Exception as e:
        return f"Error processing video: {str(e)}"