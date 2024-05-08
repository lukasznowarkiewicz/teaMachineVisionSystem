import cv2
import os
from datetime import datetime

# Ścieżka do folderu z filmami
input_folder = './'
output_folder = './outputs'

# Utworzenie folderu outputs, jeśli nie istnieje
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Wyszukiwanie plików wideo w folderze
video_files = [f for f in os.listdir(input_folder) if f.endswith('.mp4')]

# Tworzenie obiektu MOG2 do detekcji tła
mog2 = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=True)

# Przetwarzanie każdego pliku wideo w folderze
for video_file in video_files:
    video_path = os.path.join(input_folder, video_file)
    cap = cv2.VideoCapture(video_path)

    # Pobranie rozmiaru ramki i fps z obiektu kamery
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_time = 1 / fps  # czas trwania jednej klatki w sekundach

    # Definiowanie obszaru detekcji
    detection_width = 150
    detection_height = 250
    x_start = (frame_width // 2) - (detection_width // 2)
    y_start = frame_height - detection_height

    # Utworzenie nazwy wyjściowej pliku
    output_base_name = os.path.splitext(video_file)[0] + "_" + datetime.now().strftime('%Y%m%d_%H%M%S')
    output_video_file = f"{output_base_name}.mp4"
    output_csv_file = f"{output_base_name}.txt"
    output_video_path = os.path.join(output_folder, output_video_file)
    output_csv_path = os.path.join(output_folder, output_csv_file)

    # Utworzenie obiektu do zapisu wideo
    out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

    cumulative_count = 0  # Skumulowana liczba wykrytych ruchów
    active_seconds = 0.0  # Licznik aktywnych sekund

    # Czytanie pierwszej klatki
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Aplikacja MOG2 do wybranego obszaru ramki
        current_frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detection_area = current_frame_gray[y_start:y_start+detection_height, x_start:x_start+detection_width]
        fg_mask = mog2.apply(detection_area)

        # Znajdowanie konturów na masce pierwszoplanowej
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        active_in_frame = False

        for contour in contours:
            if cv2.contourArea(contour) > 100:  # Filtr na minimalny rozmiar konturu
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x_start + x, y_start + y), (x_start + x + w, y_start + y + h), (0, 255, 0), 2)
                cumulative_count += 1
                active_in_frame = True

        if active_in_frame:
            active_seconds += frame_time

        cv2.rectangle(frame, (x_start, y_start), (x_start + detection_width, y_start + detection_height), (0, 0, 255), 2)
        cv2.putText(frame, f"Detected: {cumulative_count}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, f"Seconds: {active_seconds:.2f}", (50, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        out.write(frame)

    # Zapisywanie danych do pliku CSV
    with open(output_csv_path, 'w') as f:
        f.write(f"Detected Drops,Active Time\n")
        f.write(f"{cumulative_count},{active_seconds:.2f}\n")

    # Zwolnienie zasobów
    cap.release()
    out.release()
    cv2.destroyAllWindows()

# Informacja końcowa
print(f"Przetwarzanie zakończone. Wyniki zapisano w folderze {output_folder}.")
