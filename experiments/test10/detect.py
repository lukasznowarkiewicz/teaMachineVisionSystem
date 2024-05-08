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
    output_txt_file = f"{output_base_name}.txt"
    output_video_path = os.path.join(output_folder, output_video_file)
    output_txt_path = os.path.join(output_folder, output_txt_file)

    # Create a video writer object and TXT file
    out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))
    avg_colors = []  # List to store average colors for TXT

    # Read the first frame to start processing
    ret, frame = cap.read()
    while ret:
        # Calculate the area position 50 pixels to the left from the previous position
        center_x = frame_width // 2
        center_y = frame_height // 2
        x_start = center_x - 25 - 0  # Adjust to get the middle of the 50x50 area
        y_start = center_y - 25 - 150

        # Extract the 50x50 pixel area and calculate its average color
        area = frame[y_start:y_start+50, x_start:x_start+50]
        average_color = np.mean(area, axis=(0, 1))

        # Accumulate the average color for TXT
        avg_colors.append(average_color)

        # Overlay an ellipse around the area to visualize it
        cv2.ellipse(frame, (x_start + 25, y_start + 25), (100, 50), 0, 0, 360, (0, 255, 0), 2)

        # Display current and overall average color values on the frame
        color_text = f"Current Avg Color: {int(average_color[0])}, {int(average_color[1])}, {int(average_color[2])}"
        overall_avg = np.mean(avg_colors, axis=0)
        overall_text = f"Overall Avg Color: {int(overall_avg[0])}, {int(overall_avg[1])}, {int(overall_avg[2])}"
        cv2.putText(frame, color_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, overall_text, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

        # Write the modified frame to the output file
        out.write(frame)

        # Read the next frame
        ret, frame = cap.read()

    # Write the final average color to a TXT file
    final_avg_color = np.mean(avg_colors, axis=0)
    with open(output_txt_path, 'w') as f:
        f.write("Final Average Color (R,G,B)\n")
        f.write(f"{int(final_avg_color[0])},{int(final_avg_color[1])},{int(final_avg_color[2])}\n")

    # Release resources after processing each video
    cap.release()
    out.release()

cv2.destroyAllWindows()
print("Processing complete. Output videos and TXT files are saved in the 'outputs' folder.")
