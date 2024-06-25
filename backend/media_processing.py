import cv2
from ultralytics import YOLO

# Load the YOLOv8 model
model = YOLO('backend/weights.pt')

# Process Image
def convert_image_to_text(image_path):
    try:
        # Read the image
        image = cv2.imread(image_path)

        # Check if the image is loaded correctly
        if image is None:
            return "Could not load image... Image not found...", []

        # Perform object detection on the image
        results = model(image)

        # Define predicted label list and annotations
        pred_label_list = []
        annotations = []

        # Process the results
        for result in results:
            for box in result.boxes:
                class_label = model.names[int(box.cls)]
                pred_label_list.append(class_label)

                # Draw bounding box
                xmin, ymin, xmax, ymax = map(int, box.xyxy[0])

                # Save the annotation in the annotation dict
                annotations.append({
                    "class_label": class_label,
                    "xmin": xmin,
                    "ymin": ymin,
                    "xmax": xmax,
                    "ymax": ymax
                })

        # Return the predicted labels as a concatenated string and annotations
        return ' '.join(pred_label_list), annotations
    except Exception as e:
        return f"Error processing image: {str(e)}", []

# Process Video
def convert_video_to_text(video_path):
    try:
        # Open the video file
        cap = cv2.VideoCapture(video_path)

        # Check if the video file is opened correctly
        if not cap.isOpened():
            return "Error: Could not open video file.", []

        # Total Frames
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Text storage for unique detections and annotations
        unique_text = set()
        annotations = []

        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()

            if not ret:
                break

            # Define current frame
            current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

            # Perform object detection on the frame
            results = model(frame)

            # Process detections and collect text
            current_text = ""
            frame_annotations = []

            for result in results:
                for box in result.boxes:
                    class_label = model.names[int(box.cls)]
                    current_text += class_label

                    # Draw bounding box
                    xmin, ymin, xmax, ymax = map(int, box.xyxy[0])

                    # Store the data
                    frame_annotations.append({
                        "class_label": class_label,
                        "xmin": xmin,
                        "ymin": ymin,
                        "xmax": xmax,
                        "ymax": ymax
                    })

            annotations.append({
                "frame": current_frame,
                "annotations": frame_annotations
            })

            # Add unique text to set
            unique_text.add(current_text)

            # Print progress
            progress = (current_frame / total_frames) * 100
            print(f"Progress: {progress:.2f}%)")

        # Release everything when done
        cap.release()
        cv2.destroyAllWindows()

        # Return unique text found in the video and the annotations
        return ''.join(unique_text), annotations
    except Exception as e:
        return f"Error processing video: {str(e)}", []