import cv2
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray
import sys
import time

# Ustawienia kamery
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

# Oczekiwanie na uruchomienie kamery
time.sleep(0.1)

# Ustawienie obszaru detekcji
detection_width = 150
detection_height = 250
x_start = (camera.resolution[0] // 2) - (detection_width // 2)
y_start = camera.resolution[1] - detection_height

# Inicjalizacja zmiennych
active_seconds = 0.0
cumulative_count = 0

# Odbiór obrazu z kamery
try:
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image = frame.array
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if 'prev_frame' in locals():
            detection_area = gray_image[y_start:y_start+detection_height, x_start:x_start+detection_width]
            prev_detection_area = prev_frame[y_start:y_start+detection_height, x_start:x_start+detection_width]
            frame_diff = cv2.absdiff(detection_area, prev_detection_area)
            _, thresh = cv2.threshold(frame_diff, 30, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            active_in_frame = False
            for contour in contours:
                if cv2.contourArea(contour) > 100:
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(image, (x_start + x, y_start + y), (x_start + x + w, y_start + y + h), (0, 255, 0), 2)
                    cumulative_count += 1
                    active_in_frame = True
            if active_in_frame:
                active_seconds += (1 / camera.framerate) * 4  # Czas aktywności mnożony przez 4

            sys.stdout.write(f"\rDetected Drops: {cumulative_count}, Active Time: {active_seconds:.2f} seconds")
            sys.stdout.flush()

        cv2.rectangle(image, (x_start, y_start), (x_start + detection_width, y_start + detection_height), (0, 0, 255), 2)
        cv2.imshow("Frame", image)

        key = cv2.waitKey(1) & 0xFF
        rawCapture.truncate(0)
        if key == ord("q") or key == 27:
            break

        # Zapisz aktualny obraz do przetwarzania w następnej iteracji
        prev_frame = gray_image

finally:
    cv2.destroyAllWindows()
    camera.close()
