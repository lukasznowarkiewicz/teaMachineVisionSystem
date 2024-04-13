import argparse
from picamera import PiCamera
from datetime import datetime
import time

def parse_args():
    parser = argparse.ArgumentParser(description='Nagrywanie filmów z kamery Raspberry Pi.')
    parser.add_argument('-t', '--title', type=str, required=True, help='Tytuł pliku wideo.')
    return parser.parse_args()

def main():
    args = parse_args()
    camera = PiCamera()
    camera.resolution = (640, 480)  # Ustawienie rozdzielczości wideo
    now = datetime.now()
    filename = f"{args.title}_{now.strftime('%H_%M_%d_%m_%Y')}.h264"

    try:
        # Rozpoczęcie nagrywania
        camera.start_recording(filename)
        print(f"Nagrywanie rozpoczęte. Plik: {filename}")
        
        input("Wciśnij Enter, aby zakończyć nagrywanie...")
        camera.stop_recording()
        print(f"Nagrywanie zakończone. Plik zapisany jako {filename}")
    
    finally:
        camera.close()

if __name__ == '__main__':
    main()

