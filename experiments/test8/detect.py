import cv2
import os
from datetime import datetime

input_folder = './'
output_folder = './outputs'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

video_files = [f for f in os.listdir(input_folder) if f.endswith('.mp4')]

for video_file in video_files:
    video_path = os.path.join(input_folder, video_file)
    cap = cv2.VideoCapture(video_path)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_time = 1 / fps

    detection_width = 150
    detection_height = 250
    x_start = (frame_width // 2) - (detection_width // 2)
    y_start = frame_height - detection_height

    output_base_name = os.path.splitext(video_file)[0] + "_" + datetime.now().strftime('%Y%m%d_%H%M%S')
    output_video_file = f"{output_base_name}.mp4"
    output_csv_file = f"{output_base_name}.txt"
    output_video_path = os.path.join(output_folder, output_video_file)
    output_csv_path = os.path.join(output_folder, output_csv_file)

    out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

    cumulative_count = 0
    active_seconds = 0.0

    ret, prev_frame = cap.read()
    if ret:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            equalized_frame = cv2.equalizeHist(gray_frame)

            sobelx = cv2.Sobel(equalized_frame, cv2.CV_64F, 1, 0, ksize=5)

            _, thresholded = cv2.threshold(sobelx, 50, 255, cv2.THRESH_BINARY)

            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            dilated = cv2.dilate(thresholded, kernel, iterations=2)

            contours, _ = cv2.findContours(dilated.astype('uint8'), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            active_in_frame = False

            for contour in contours:
                if cv2.contourArea(contour) > 50:
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cumulative_count += 1
                    active_in_frame = True

            if active_in_frame:
                active_seconds += frame_time

            cv2.rectangle(frame, (x_start, y_start), (x_start + detection_width, y_start + detection_height), (0, 0, 255), 2)
            cv2.putText(frame, f"Detected: {cumulative_count}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(frame, f"Seconds: {active_seconds:.2f}", (50, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            out.write(frame)

        with open(output_csv_path, 'w') as f:
            f.write(f"Detected Drops,Active Time\n")
            f.write(f"{cumulative_count},{active_seconds:.2f}\n")

        cap.release()
        out.release()
        cv2.destroyAllWindows()
    else:
        print(f"Nie udało się wczytać wideo {video_file}.")
