import cv2
import numpy as np
import time

def calculate_ellipse_perimeter(axes):
    a, b = axes[0] / 2, axes[1] / 2  # średnie długości osi
    perimeter = np.pi * (3*(a + b) - np.sqrt((3*a + b) * (a + 3*b)))
    return perimeter

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Nie można otworzyć kamery.")
        exit()

    fps_limit = 5
    time_frame = 1.0 / fps_limit

    try:
        last_time = time.time()
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Nie można odczytać strumienia z kamery.")
                break

            if (time.time() - last_time) > time_frame:
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Stosowanie erozji i dylatacji
                kernel = np.ones((5, 5), np.uint8)
                eroded_frame = cv2.erode(gray_frame, kernel, iterations=1)
                dilated_frame = cv2.dilate(eroded_frame, kernel, iterations=1)

                edges = cv2.Canny(dilated_frame, 50, 150)

                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    if cv2.arcLength(contour, True) > 800 and len(contour) >= 5:
                        try:
                            ellipse = cv2.fitEllipse(contour)
                            perimeter = calculate_ellipse_perimeter(ellipse[1])
                            if perimeter > 500:
                                cv2.ellipse(frame, ellipse, (0, 255, 0), 2)
                        except:
                            pass

                cv2.imshow('Detekcja krawędzi', edges)
                cv2.imshow('Wykrywanie łuku', frame)
                last_time = time.time()

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
