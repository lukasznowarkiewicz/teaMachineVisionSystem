import cv2
import numpy as np
import time

# Wczytanie wag i konfiguracji modelu YOLO
net = cv2.dnn.readNet('yolov4-tiny.weights', 'yolov4-tiny.cfg')

# Ustawienie nazw klas
classes = []
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

# Ustawienie parametrów kamery
cap = cv2.VideoCapture(0)

# Ustawienie parametrów modelu
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# Ograniczenie do 5 fps
frame_rate = 25
prev = 0

# Przetwarzanie tylko co trzeciej klatki
frame_skip = 3
frame_count = 0

while True:
    ret, frame = cap.read()
    
    if not ret or frame_count % frame_skip != 0:
        frame_count += 1
        continue
    
    frame_count += 1
    time_elapsed = time.time() - prev
    if time_elapsed > 1./frame_rate:
        prev = time.time()
        
        # Obrót obrazu o 180 stopni
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        
        # Zmniejszenie rozdzielczości obrazu do 320x240
        frame = cv2.resize(frame, (160, 120))
        
        height, width, channels = frame.shape

        # Detekcja obiektów z użyciem zmniejszonego bloba
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (160, 120), (0, 0, 0), True, crop=False)
        net.setInput(blob)
        outs = net.forward(output_layers)

        # Informacje o wykrytych obiektach
        class_ids = []
        confidences = []
        boxes = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    # Obiekt wykryty
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    # Koordynaty prostokąta
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        # Zastosowanie non-max suppression
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

        # Rysowanie prostokątów i wyświetlanie wyników
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(classes[class_ids[i]])
                if label == 'cup':
                    print("Kubek wykryty!")
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, label, (x, y + 30), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
        
        # Wyświetlanie obrazu z kamery
        cv2.imshow("Image", frame)
    
    key = cv2.waitKey(1)
    if key == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
