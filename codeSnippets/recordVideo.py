import argparse
from picamera import PiCamera
from datetime import datetime
import subprocess
import time

def parse_args():
    parser = argparse.ArgumentParser(description='Nagrywanie filmów z kamery Raspberry Pi i zapis jako MP4.')
    parser.add_argument('-t', '--title', type=str, required=True, help='Tytuł pliku wideo.')
    return parser.parse_args()

def main():
    args = parse_args()
    camera = PiCamera()
    camera.resolution = (640, 480)  # Ustawienie rozdzielczości wideo
    now = datetime.now()
    temp_filename = f"{args.title}_{now.strftime('%H_%M_%d_%m_%Y')}.h264"
    final_filename = f"{args.title}_{now.strftime('%H_%M_%d_%m_%Y')}.mp4"

    try:
        # Rozpoczęcie nagrywania
        camera.start_recording(temp_filename)
        print(f"Nagrywanie rozpoczęte. Plik tymczasowy: {temp_filename}")
        
        input("Wciśnij Enter, aby zakończyć nagrywanie...")
        camera.stop_recording()
        print("Nagrywanie zakończone, trwa konwersja do MP4...")
    
    finally:
        camera.close()

    # Konwersja pliku do formatu MP4
    convert_command = f"ffmpeg -framerate 24 -i {temp_filename} -c copy {final_filename}"
    subprocess.run(convert_command.split())
    print(f"Plik zapisany jako {final_filename}")

    # Usuwanie tymczasowego pliku .h264
    remove_command = f"rm {temp_filename}"
    subprocess.run(remove_command.split())
    print(f"Tymczasowy plik {temp_filename} usunięty.")

if __name__ == '__main__':
    main()

