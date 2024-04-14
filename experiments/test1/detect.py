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

    # Utworzenie nazwy wyjściowej pliku
    output_file_name = f"{os.path.splitext(video_files[0])[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
    output_path = os.path.join(output_folder, output_file_name)

    # Utworzenie obiektu do zapisu wideo
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc('M','J','P','G'), fps, (frame_width, frame_height))

    # Czytanie pierwszej klatki
    ret, prev_frame = cap.read()

    if ret:
        prev_frame_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

        # Pętla przez wszystkie klatki wideo
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Konwersja klatki do skali szarości
            current_frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Oblicz różnicę między aktualną a poprzednią klatką
            frame_diff = cv2.absdiff(current_frame_gray, prev_frame_gray)

            # Zastosuj progowanie, aby uzyskać wyraźniejsze wyniki
            _, thresh = cv2.threshold(frame_diff, 30, 255, cv2.THRESH_BINARY)

            # Znajdowanie konturów na obrazie progowanym
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Rysowanie konturów na oryginalnym obrazie
            for contour in contours:
                if cv2.contourArea(contour) > 100:  # minimalny rozmiar obszaru
                    x, y, w, h = cv2.boundingRe ct(contour)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

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

