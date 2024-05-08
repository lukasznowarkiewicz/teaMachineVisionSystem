import cv2
import os
import numpy as np
from datetime import datetime

# Define the paths for input and output folders
input_folder = './'
output_folder = './outputs'

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
    output_video_path = os.path.join(output_folder, output_video_file)

    # Create a video writer object to save the output video
    out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

    # Read the first frame to start processing
    ret, frame = cap.read()
    while ret:
        # Calculate the area position 100 pixels to the right and 100 pixels up from the center
        center_x = frame_width // 2
        center_y = frame_height // 2
        x_start = center_x - 5 + 100  # Adjust to get the middle of the 10x10 area
        y_start = center_y - 5 - 100  # Adjust to get the middle of the 10x10 area

        # Extract the 10x10 pixel area and calculate its average color
        area = frame[y_start:y_start+10, x_start:x_start+10]
        average_color = np.mean(area, axis=(0, 1))

        # Overlay a rectangle around the area to visualize it
        cv2.rectangle(frame, (x_start, y_start), (x_start + 10, y_start + 10), (0, 255, 0), 2)

        # Put the average color value as text on the frame
        color_text = f"Avg Color: {int(average_color[0])}, {int(average_color[1])}, {int(average_color[2])}"
        cv2.putText(frame, color_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # Write the modified frame to the output file
        out.write(frame)

        # Read the next frame
        ret, frame = cap.read()

    # Release resources after processing each video
    cap.release()
    out.release()

cv2.destroyAllWindows()
print("Processing complete. Output videos are saved in the 'outputs' folder.")
