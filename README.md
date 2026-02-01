# Interaktywny Notatnik Głosowy (Voice Notebook)

Aplikacja desktopowa umożliwiająca zarządzanie notatkami za pomocą komend głosowych w języku naturalnym. Projekt wykorzystuje model **Llama 3** (przez Groq API) do interpretacji intencji użytkownika oraz **Google Speech Recognition** do transkrypcji mowy.

**Autor:** Piotr Walerianowicz

## Funkcjonalności

- **Sterowanie głosem:** Dodawanie, usuwanie, edycja i oznaczanie zrobionych notatek bez użycia klawiatury.
- **Inteligencja (NLP):** Rozumienie mowy potocznej (np. "Weź wywal to o zakupach" -> Usunięcie notatki).
- **Zarządzanie notatnikami:** Tworzenie wielu notatników na notatki.
- **Interfejs GUI:** Przejrzysty interfejs okienkowy zbudowany w Tkinter.
- **Filtrowanie:** Widok tylko zadań wykonanych / do zrobienia.

## Technologie

Projekt został zrealizowany w języku **Python 3.10+**.

- **GUI:** `tkinter`
- **Speech-to-Text (STT):** `SpeechRecognition` (Wrapper na Google API)
- **Logika AI (LLM):** `Groq API` (Model: Llama 3.3 70b)
- **Audio:** `PyAudio`

## Instrukcja Instalacji

1. **Instalacja bibliotek:**
   ```bash
   pip install -r requirements.txt
   
2. **Konfiguracja API:**

- **Pobierz klucz:** `console.groq.com`
- **Utwórz plik .env w folderze projektu i wpisz:** `GROQ_API_KEY=tu_wklej_twoj_klucz`

3. **Uruchomienie:**
    ```bash
   python main.py