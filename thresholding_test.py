import cv2 as cv
import numpy as np

cap = cv.VideoCapture(0)

if not cap.isOpened():
    print("Błąd: Nie udało się otworzyć kamerki.")
    exit()

print("Kamera uruchomiona. Wciśnij 'q', aby wyjść.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Błąd: Nie można pobrać klatki. Zamykanie...")
        break 
    
    # 1. Przygotowanie obrazu (szarość + rozmycie)
    gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    blurred = cv.GaussianBlur(gray_frame, (7, 7), 0)
    
    # 2. Detekcja krawędzi (Canny zamiast Threshold)
    # Wartości 50 i 150 to progi (dolny i górny) detekcji. Możesz je zmieniać.
    edges = cv.Canny(blurred, 50, 150)
    
    # 3. Probabilistyczna Transformata Hougha
    lines = cv.HoughLinesP(
        edges, 
        rho=1,                # Rozdzielczość odległości w pikselach
        theta=np.pi/180,      # Rozdzielczość kątowa w radianach (tutaj 1 stopień)
        threshold=50,         # Minimalna liczba przecięć, by uznać to za linię
        minLineLength=60,     # Minimalna długość linii w pikselach
        maxLineGap=10         # Maksymalna przerwa między segmentami, by złączyć je w jedną linię
    )
    
    # Tworzymy kopię oryginalnej klatki, na której narysujemy wyniki
    output_frame = frame.copy()
    
    # 4. Rysowanie wykrytych linii na obrazie wyjściowym
    # Upewniamy się, że algorytm w ogóle znalazł jakieś linie (lines is not None)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            # cv.line(obraz, start, koniec, kolor(B,G,R), grubość)
            cv.line(output_frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

    # Wyświetlanie okien
    cv.imshow('Krawedzie (Canny)', edges)
    cv.imshow('Wykryte linie (Hough)', output_frame)
    
    if cv.waitKey(1) == ord('q'):
        break

cap.release()
cv.destroyAllWindows()