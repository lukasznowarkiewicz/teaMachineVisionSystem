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

# Wczytanie pierwszego filmu z listy
if video_files:
    video_path = os.path.join(input_folder, video_files[0])
    cap = cv2.VideoCapture(video_path)

    # Pobranie rozmiaru ramki i fps z obiektu kamery
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Definiowanie obszaru detekcji
    detection_width = 150
    detection_height = 250
    x_start = (frame_width // 2) - (detection_width // 2)
    y_start = frame_height - detection_height

    # Utworzenie nazwy wyjściowej pliku
    output_file_name = f"{os.path.splitext(video_files[0])[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    output_path = os.path.join(output_folder, output_file_name)

    # Utworzenie obiektu do zapisu wideo
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

    # Czytanie pierwszej klatki
    ret, prev_frame = cap.read()
    cumulative_count = 0  # Skumulowana liczba wykrytych różnic

    if ret:
        prev_frame_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

        # Pętla przez wszystkie klatki wideo
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Konwersja klatki do skali szarości
            current_frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Ograniczenie obszaru detekcji
            detection_area = current_frame_gray[y_start:y_start+detection_height, x_start:x_start+detection_width]
            prev_detection_area = prev_frame_gray[y_start:y_start+detection_height, x_start:x_start+detection_width]

            # Oblicz różnicę między aktualną a poprzednią klatką w obszarze detekcji
            frame_diff = cv2.absdiff(detection_area, prev_detection_area)

            # Zastosuj progowanie, aby uzyskać wyraźniejsze wyniki
            _, thresh = cv2.threshold(frame_diff, 30, 255, cv2.THRESH_BINARY)

            # Znajdowanie konturów na obrazie progowanym
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Rysowanie konturów na oryginalnym obrazie
            for contour in contours:
                if cv2.contourArea(contour) > 100:  # minimalny rozmiar obszaru
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(frame, (x_start + x, y_start + y), (x_start + x + w, y_start + y + h), (0, 255, 0), 2)
                    cumulative_count += 1  # Aktualizacja licznika

            # Obrysowanie czerwonym prostokątem całego obszaru detekcji
            cv2.rectangle(frame, (x_start, y_start), (x_start + detection_width, y_start + detection_height), (0, 0, 255), 2)

            # Wyświetlanie skumulowanej liczby wykrytych różnic
            cv2.putText(frame, f"Detected: {cumulative_count}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

            # Zapisz ramkę w pliku wyjściowym
            out.write(frame)

            # Przygotuj się na kolejną iterację
            prev_frame_gray = current_frame_gray
    else:
        print("Nie udało się wczytać wideo.")

    # Zwolnienie zasobów
    cap.release()
    out.release()
    cv2.destroyAllWindows()
else:
    print("Nie znaleziono plików wideo w folderze.")
