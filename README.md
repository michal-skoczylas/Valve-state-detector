# Valve Detector 🚰

Zaawansowany system do detekcji stanu zaworów (Otwarty/Zamknięty) wykorzystujący analizę obrazu na żywo za pomocą OpenCV z nowoczesnym interfejsem graficznym napisanym w Vue 3.

## 🌟 Funkcje

- **Rozpoznawanie Wizyjne:** System wykorzystuje OpenCV w backendzie do analizowania strumieni wideo z lokalnych kamer (lub wczytanych obrazów statycznych).
- **Detekcja Kolorów (HSV):** Konfigurowalna detekcja stanu na podstawie filtrowania palety barw (Hue, Saturation, Value).
- **Wielokrotne Strefy (ROI):** Możliwość ręcznego nakreślania wielu Stref Zainteresowania (Region of Interest) w obszarze działania kamery z osobnym konfigurowaniem logiki detekcji.
- **Wygładzanie Morfologiczne:** Operacje otwarcia i zamknięcia na masce ułatwiające redukcję szumów.
- **Zarządzanie Zestawami (Config):** Zapis i wczytywanie stworzonych stref (ROI) i suwaków parametrów w formacie JSON.
- **Nowoczesny Panel Vue 3:** Oddzielny, lekki i w pełni interaktywny Frontend (SFC, Vite), serwowany obok API.

---

## 🛠️ Technologie

Projekt dzieli się na dwa główne moduły (Backend & Frontend):

**Backend:**
- **Python 3**
- **Flask** (wraz z wtyczką `flask-cors` do obsługi REST API)
- **OpenCV (`cv2`)** i **Numpy** (Przetwarzanie i analiza obrazów)

**Frontend:**
- **Vue 3** (w podejściu Composition API)
- **Vite** (jako system budowania projektów HMR)
- **Axios** (do asynchronicznej komunikacji z backendem)

---

## 🚀 Jak uruchomić?

Dzięki skryptowi startowemu `start.sh`, możesz łatwo podnieść oba serwery jednocześnie.

### Wymagania przed pierwszym uruchomieniem
Zainstaluj paczki w Pythonie:
```bash
pip install flask opencv-python numpy flask-cors
```
Zainstaluj paczki na Frontendzie (korzystając z Node.js):
```bash
cd frontend
npm install
cd ..
```

### Uruchomienie deweloperskie
W głównym katalogu projektu wywołaj komendę:
```bash
./start.sh
```

- **Backend (Flask)** uruchomi się na `http://127.0.0.1:5000`
- **Frontend (Vite)** uruchomi się na `http://localhost:5173` i użyje systemu Proxy do komunikacji z serwerem. 

Aby zamknąć cały system, po prostu naciśnij `Ctrl+C` w tym samym terminalu.

---

## 📸 Instrukcja Użytkowania

1. **Źródło obrazu:** Wybierz w lewym menu podłączoną kamerę fizyczną (zacznie świecić na czerwono `🔴 Camera X`) lub zapisane statyczne zdjęcie z folderu `images/`.
2. **Dodawanie Zaworów (ROI):** Na panelu ze zdjęciem przytrzymaj lewy przycisk myszy i przeciągnij, aby utworzyć obszar badawczy (kwadrat). System stworzy nową kartę dla tego zaworu.
3. **Pobieranie wartości H:** Kliknięcie pojedynczym pikselem na kamerze ustawi kolor odniesienia (wartości Hue, Saturation, Value).
4. **Edycja Logiki:** Użyj suwaków detekcji koloru (Tolerancja, Filtrowanie, Pokrycie). Wciskając ikonkę `⚙️ Edytuj` na kafelkach zaworów, możesz zmieniać ich nazwę oraz ustalać logikę NO/NC (Normalnie Otwarty / Normalnie Zamknięty względem detekcji koloru).
5. **Zapis Profilu:** Wprowadź nazwę profilu konfiguracyjnego z lewej strony i zapisz stan systemu, aby móc go łatwo wznowić przy następnym uruchomieniu.
