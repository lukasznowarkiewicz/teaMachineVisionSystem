import cv2
import os
import csv
import concurrent.futures

input_folder = './'
output_folder = './outputs'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

video_files = [f for f in os.listdir(input_folder) if f.endswith('.h264')]

def process_frame(current_frame_gray, previous_frame_gray):
    frame_diff = cv2.absdiff(current_frame_gray, previous_frame_gray)
    _, thresh = cv2.threshold(frame_diff, 30, 255, cv2.THRESH_BINARY)
    thresh = cv2.dilate(thresh, None, iterations=2)
    return thresh

pixel_to_mm_ratio = (31 / 720) ** 2

def process_video(video_file):
    video_path = os.path.join(input_folder, video_file)
    cap = cv2.VideoCapture(video_path)
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    temp_video_path = os.path.join(output_folder, os.path.splitext(video_file)[0] + '_temp.mp4')
    output_video_path = os.path.join(output_folder, os.path.splitext(video_file)[0] + '_processed.mp4')
    output_txt_path = os.path.join(output_folder, os.path.splitext(video_file)[0] + '_data.txt')
    
    out = cv2.VideoWriter(temp_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))
    total_area_mm2 = 0

    ret, previous_frame = cap.read()
    if not ret:
        print(f"Nie udało się wczytać wideo {video_file}.")
        cap.release()
        return (video_file, total_area_mm2)
        
    previous_frame_gray = cv2.cvtColor(previous_frame, cv2.COLOR_BGR2GRAY)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        current_frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mask = process_frame(current_frame_gray, previous_frame_gray)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        frame_area_pixels = sum(cv2.contourArea(contour) for contour in contours if cv2.contourArea(contour) > 10)
        frame_area_mm2 = frame_area_pixels * pixel_to_mm_ratio
        total_area_mm2 += frame_area_mm2

        for contour in contours:
            if cv2.contourArea(contour) > 10:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        text = f"Area this frame: {frame_area_mm2:.2f} mm^2, Total Area: {total_area_mm2:.2f} mm^2"
        cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        out.write(frame)
        previous_frame_gray = current_frame_gray

    cap.release()
    out.release()

    # Compress the video to 480x480
    cap = cv2.VideoCapture(temp_video_path)
    out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (480, 480))

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        resized_frame = cv2.resize(frame, (480, 480))
        out.write(resized_frame)

    cap.release()
    out.release()
    os.remove(temp_video_path)

    # Write to individual text file
    with open(output_txt_path, 'w') as f:
        f.write(f"Total Area in mm^2: {total_area_mm2:.2f}\n")

    return (video_file, total_area_mm2)

# Open the CSV file for writing results
summary_csv_path = os.path.join(output_folder, 'summary_results.csv')
with open(summary_csv_path, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['Video File', 'Total Area (mm^2)'])

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_video, video_file) for video_file in video_files]
        for future in concurrent.futures.as_completed(futures):
            video_file, total_area_mm2 = future.result()
            csvwriter.writerow([video_file, f"{total_area_mm2:.2f}"])

cv2.destroyAllWindows()
