import os
from datetime import datetime

import json


class Note:
    def __init__(self, text, done=False, date=None):
        self.text = text
        self.done = done
        self.date = date if date else datetime.now().strftime("%Y-%m-%d %H:%M")

    def to_dict(self):
        return {"text": self.text, "done": self.done, "date": self.date}

class NoteBook:
    def __init__(self):
        self.notes = []

    # Dodaje nową notatkę do listy
    def add_note(self, text):
        if not text.strip():
            return False
        # Automatyczna duża litera:
        formatted_text = text.strip()[0].upper() + text.strip()[1:]
        self.notes.append(Note(formatted_text))
        return True

    # Usuwa notatkę o konkretnym numerze i przesuwa resztę listy
    def remove_note(self, index):
        if 0 <= index < len(self.notes):
            del self.notes[index]
            return True
        return False

    # Usuwa z listy wszystkie notatki oznaczone jako "zrobione"
    def clean_done(self):
        self.notes = [n for n in self.notes if not n.done]
        return True

    # Zmienia treść istniejącej już notatki pod wskazanym indeksem
    def edit_note(self, index, new_text):
        if 0 <= index < len(self.notes):
            self.notes[index].text = new_text
            return True
        return False

    # Przełącza status notatki między "zrobione" a "do zrobienia"
    def toggle_done(self, index):
        if 0 <= index < len(self.notes):
            self.notes[index].done = not self.notes[index].done
            return True
        return False

    # Zwraca pełną listę wszystkich obiektów notatek w tym notatniku
    def list_notes(self):
        return self.notes


class NoteBookManager:
    def __init__(self):
        self.notebooks = {}
        self.current = None
        self.filename = "data.json"
        self.load_data()

    # Tworzy nową szufladę na notatki o podanej nazwie
    def add_notebook(self, name):
        if not name:
            return False
        key = name.lower().strip()
        if key in self.notebooks:
            return False

        self.notebooks[key] = NoteBook()
        if self.current is None:
            self.current = key
        return True

    def remove_notebook(self, name):
        # Zabezpieczenie: nie usuwaj, jeśli to jedyny notatnik
        if len(self.notebooks) <= 1:
            return False

        key = name.lower().strip()
        if key in self.notebooks:
            del self.notebooks[key]

            # Jeśli usunęliśmy ten, który był otwarty, przełącz na pierwszy dostępny
            if self.current == key:
                self.current = list(self.notebooks.keys())[0]

            self.save_data()
            return True
        return False

    # Zmienia aktualnie wyświetlany notatnik na inny istniejący
    def switch(self, name):
        key = name.lower().strip()
        if key in self.notebooks:
            self.current = key
            return True
        return False

    # Zwraca obiekt notatnika, na którym aktualnie pracujemy
    def get_current(self):
        return self.notebooks[self.current]

    # Szuka w notatniku pierwszej notatki, która zawiera w treści podane słowo
    def find_note_by_text(self, query):
        notes = self.get_current().list_notes()
        # Konwertuje na string na wypadek, gdyby LLM wysłało int
        search_term = str(query).lower()

        for i, note in enumerate(notes):
            if search_term in note.text.lower():
                return i
        return None

    def save_data(self):
        data = {}
        for name, nb in self.notebooks.items():
            data[name] = [n.to_dict() for n in nb.notes]

        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_data(self):
        if not os.path.exists(self.filename):
            return
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                for name, notes_data in data.items():
                    self.add_notebook(name)
                    self.notebooks[name].notes = []
                    for n in notes_data:
                        self.notebooks[name].notes.append(
                            Note(n["text"], n["done"], n.get("date"))
                        )
        except Exception as e:
            print(f"Błąd odczytu: {e}")

manager = NoteBookManager()
manager.add_notebook("Domyślny")
notebook = manager.get_current()