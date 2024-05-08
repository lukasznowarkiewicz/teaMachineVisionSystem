import argparse
import cv2
from datetime import datetime
import subprocess
import time

def parse_args():
    parser = argparse.ArgumentParser(description='Nagrywanie filmów z kamery USB i zapis jako MP4.')
    parser.add_argument('-t', '--title', type=str, required=True, help='Tytuł pliku wideo.')
    return parser.parse_args()

def main():
    args = parse_args()
    cap = cv2.VideoCapture(0)  # Tworzenie obiektu VideoCapture używającego pierwszej kamery USB
    if not cap.isOpened():
        raise IOError("Nie można otworzyć kamery.")
    
    # Ustawienie rozdzielczości wideo
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 24)  # Ustawienie liczby klatek na sekundę

    now = datetime.now()
    temp_filename = f"{args.title}_{now.strftime('%H_%M_%d_%m_%Y')}.avi"
    final_filename = f"{args.title}_{now.strftime('%H_%M_%d_%m_%Y')}.mp4"

    # Rozpoczęcie nagrywania do pliku AVI za pomocą kodeka MJPEG
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(temp_filename, fourcc, 24.0, (640, 480))

    print(f"Nagrywanie rozpoczęte. Plik tymczasowy: {temp_filename}")
    input("Wciśnij Enter, aby zakończyć nagrywanie...")

    while True:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
        else:
            break

    # Zakończenie nagrywania
    cap.release()
    out.release()
    print("Nagrywanie zakończone, trwa konwersja do MP4...")

    # Konwersja pliku do formatu MP4
    convert_command = f"ffmpeg -i {temp_filename} -c:v libx264 {final_filename}"
    subprocess.run(convert_command.split())
    print(f"Plik zapisany jako {final_filename}")

    # Usuwanie tymczasowego pliku .avi
    remove_command = f"rm {temp_filename}"
    subprocess.run(remove_command.split())
    print(f"Tymczasowy plik {temp_filename} usunięty.")

if __name__ == '__main__':
    main()

