import cv2
from ultralytics import YOLO

model = YOLO('backend/weights.pt')

# Process Image
def convert_image_to_text(image_path):
    try:

        image = cv2.imread(image_path)

        if image is None:
            return "Could not load image... Image not found...", []

        results = model(image)

        pred_label_list = []
        annotations = []

        for result in results:
            for box in result.boxes:
                class_label = model.names[int(box.cls)]
                pred_label_list.append(class_label)

                xmin, ymin, xmax, ymax = map(int, box.xyxy[0])

                annotations.append({
                    "class_label": class_label,
                    "xmin": xmin,
                    "ymin": ymin,
                    "xmax": xmax,
                    "ymax": ymax
                })

        return ' '.join(pred_label_list), annotations
    except Exception as e:
        return f"Error processing image: {str(e)}", []

# Process Video
def convert_video_to_text(video_path):
    try:

        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            return "Error: Could not open video file.", []

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        unique_text = set()
        annotations = []

        while True:
            ret, frame = cap.read()

            if not ret:
                break

            current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

            results = model(frame)

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

            unique_text.add(current_text)

            progress = (current_frame / total_frames) * 100
            print(f"Progress: {progress:.2f}%)")

        cap.release()
        cv2.destroyAllWindows()

        return ''.join(unique_text), annotations
    except Exception as e:
        return f"Error processing video: {str(e)}", []