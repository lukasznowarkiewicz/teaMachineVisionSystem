import cv2
import numpy as np
import os
from datetime import datetime

# Paths to YOLO weights and config files
model_weights = 'yolov3.weights'
model_cfg = 'yolov3.cfg'
coco_names = 'coco.names'

# Load YOLO model
net = cv2.dnn.readNetFromDarknet(model_cfg, model_weights)
classes = []
with open(coco_names, 'r') as f:
    classes = f.read().splitlines()

# Define the paths for input and output folders
input_folder = './'
output_folder = './outputs'

# Constants to convert pixels to cm
pixels_per_cm_x = 45  # Number of pixels in 1 cm on the x-axis
pixels_per_cm_y = 45  # Number of pixels in 1 cm on the y-axis

# Create the output folder if it does not exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Find all mp4 files in the input folder
video_files = [f for f in os.listdir(input_folder) if f.endswith('.mp4')]

# Process each video file
for video_file in video_files:
    video_path = os.path.join(input_folder, video_file)
    cap = cv2.VideoCapture(video_path)

    # Get frame dimensions and frames per second from the video
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Define the output video filename with a timestamp
    output_base_name = os.path.splitext(video_file)[0] + "_" + datetime.now().strftime('%Y%m%d_%H%M%S')
    output_video_file = f"{output_base_name}.mp4"
    output_txt_file = f"{output_base_name}.txt"
    output_video_path = os.path.join(output_folder, output_video_file)
    output_txt_path = os.path.join(output_folder, output_txt_file)

    # Create a video writer object
    out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

    # Initialize list to store dimensions and volumes
    dimensions = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        height, width, _ = frame.shape
        blob = cv2.dnn.blobFromImage(frame, 1/255, (416, 416), (0, 0, 0), swapRB=True, crop=False)
        net.setInput(blob)
        output_layers_names = net.getUnconnectedOutLayersNames()
        layerOutputs = net.forward(output_layers_names)

        boxes = []
        confidences = []
        class_ids = []

        for output in layerOutputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

            indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        if len(indexes) > 0:
            indexes = indexes.flatten()  # Ensure indexes are flattened properly
            for i in indexes:
                x, y, w, h = boxes[i]
                label = str(classes[class_ids[i]])
                if label == "cup":
                    # Draw the full bounding box in green
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, f'{label} {int(confidences[i]*100)}%', (x, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                    # Assuming the handle is on the left and occupies 40% of the width
                    handle_width = int(w * 0.3)
                    effective_width = w - handle_width

                    # Draw the effective area without handle in black
                    cv2.rectangle(frame, (x + handle_width, y), (x + w, y + h), (0, 0, 0), 2)
                    width_cm = effective_width / pixels_per_cm_x
                    height_cm = h / pixels_per_cm_y
                    volume_cm3 = np.pi * (width_cm / 2) ** 2 * height_cm
                    cv2.putText(frame, f'{width_cm:.2f}cm x {height_cm:.2f}cm, Vol: {volume_cm3:.2f}cm^3', (x + handle_width, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

                    # Save dimensions for averaging
                    dimensions.append((width_cm, height_cm, volume_cm3))

        out.write(frame)


    # Release video writer and capture objects
    cap.release()
    out.release()

    # Calculate average dimensions and volume
    if dimensions:
        avg_width = sum(d[0] for d in dimensions) / len(dimensions)
        avg_height = sum(d[1] for d in dimensions) / len(dimensions)
        avg_volume = sum(d[2] for d in dimensions) / len(dimensions)*0.9 # 0.9 because of wall thickness 
        with open(output_txt_path, 'w') as f:
            f.write(f'Average Width: {avg_width:.2f} cm\n')
            f.write(f'Average Height: {avg_height:.2f} cm\n')
            f.write(f'Average Volume: {avg_volume:.2f} cm³\n')

cv2.destroyAllWindows()
print("Processing complete. Output videos and TXT files are saved in the 'outputs' folder.")
