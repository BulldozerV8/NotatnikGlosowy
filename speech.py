import speech_recognition as sr
from tkinter import messagebox

# Nagrywa dźwięk z mikrofonu i zamienia go na tekst przez Google Speech
def get_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            # Kalibracja szumów otoczenia
            r.adjust_for_ambient_noise(source, duration=0.2)
            # Zwiększamy czas oczekiwania na koniec zdania
            r.pause_threshold = 2.0
            r.energy_threshold = 200
            audio = r.listen(source, timeout=5, phrase_time_limit=None)

            return r.recognize_google(audio, language="pl-PL")
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except:
            return None

