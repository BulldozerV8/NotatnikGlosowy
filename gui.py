import tkinter as tk
from tkinter import messagebox

from llm import interpret_command
from models import manager
from speech import get_speech

class Application:

    def __init__(self, root):
        self.root = root
        self.root.title("NoteBook")

        self.filter_mode = "all"
        self.visible_map = []
        self.last_added_index = None

        self.nb_var = tk.StringVar()
        self.nb_menu = tk.OptionMenu(root, self.nb_var, "")
        self.nb_menu.grid(row=0, column=0)
        tk.Button(root, text="Nowy notatnik", command=self.add_notebook)\
            .grid(row=0, column=1)
        tk.Button(root, text="Usuń ten notatnik", command=self.remove_notebook_btn, bg="#ffcccc") \
            .grid(row=0, column=2, padx=5)

        self.entry = tk.Entry(root, width=50)
        self.entry.grid(row=1, column=0, columnspan=3, pady=5)

        self.listbox = tk.Listbox(root, width=60, height=15)
        self.listbox.grid(row=2, column=0, columnspan=3)

        tk.Button(root, text="Dodaj", command=self.add_note).grid(row=3, column=0)
        tk.Button(root, text="Usuń", command=self.remove_note).grid(row=3, column=1)
        tk.Button(root, text="Zrobione", command=self.toggle_done).grid(row=3, column=2)
        tk.Button(root, text="Edytuj", command=self.edit_note).grid(row=4, column=0)
        tk.Button(root, text="Wyczysc", command=self.clean_done).grid(row=4, column=1)


        self.voice_btn = tk.Button(root, text="Mów", width=20, command=self.handle_voice_command)
        self.voice_btn.grid(row=6, column=0, padx=5, pady=5)

        tk.Button(root, text="Pomoc", command=self.show_help).grid(row=0, column=3, padx=5)

        tk.Label(root, text="Filtr:").grid(row=4, column=2, sticky="e")

        self.filter_var = tk.StringVar(value="Wszystkie")
        self.filter_menu = tk.OptionMenu(root, self.filter_var, "Wszystkie", "Zrobione", "Do zrobienia",
                                         command=self.on_filter_change)
        self.filter_menu.grid(row=4, column=2, sticky="ew")



        self.refresh_notebook_menu()
        self.refresh()

    def show_help(self):
        help_text = (
            "Komendy głosowe i tekstowe:\n"
            "- Dodaj notatkę: dodaj <treść>\n"
            "- Edytuj notatkę: edytuj <id> <nowa treść>\n"
            "- Usuń notatkę: usuń <id>\n"
            "- Zaznacz wykonanie: zrobione <id>\n"
            "- Usun wykonane: wyczysc\n"
            "- Zmiana notatnika: przełącz na <treść>\n"
            "- Nowy notatnika: nowy notatnik <treść>\n"
            "- Filtruj: filtruj zrobione/niezrobione/wszystkie\n"
        )
        messagebox.showinfo("Pomoc", help_text)

    def on_filter_change(self, value):
        mapping = {"Wszystkie": "all", "Zrobione": "done", "Do zrobienia": "todo"}
        self.set_filter(mapping.get(value, "all"))

    # Aktualizuje nazwy notatników w rozwijanym menu u góry okna
    def refresh_notebook_menu(self):
        menu = self.nb_menu["menu"]
        menu.delete(0, "end")
        for name in manager.notebooks:
            menu.add_command(
                label=name,
                command=lambda n=name: self.switch_notebook(n)
            )
        self.nb_var.set(manager.current)

    # Odświeża widok listy, uwzględniając filtry i kolorując ostatnią zmianę
    def refresh(self):
        self.listbox.delete(0, tk.END)
        self.visible_map.clear()

        notes = manager.get_current().list_notes()

        for i, note in enumerate(notes):
            if self.filter_mode == "done" and not note.done:
                continue
            if self.filter_mode == "todo" and note.done:
                continue

            #idx = len(self.visible_map) + 1
            idx = i + 1
            status = "✓" if note.done else "✗"
            self.listbox.insert(tk.END, f"{idx}: {note.text}   (dodano: {note.date}) [{status}]")
            self.visible_map.append(i)

            if i == self.last_added_index:
                self.listbox.itemconfig(len(self.visible_map) - 1, {'bg': '#ffffcc'})
            if note.done:
                self.listbox.itemconfig(len(self.visible_map) - 1, {'fg': 'gray'})

    # Sprawdza, który element na liście został kliknięty myszką
    def get_selected_index(self):
        try:
            return self.visible_map[self.listbox.curselection()[0]]
        except:
            return None

    # Pobiera tekst z pola wpisywania i tworzy nową notatkę
    def add_note(self):
        if manager.get_current().add_note(self.entry.get()):
            self.last_added_index = len(manager.get_current().list_notes()) - 1
            self.entry.delete(0, tk.END)
            manager.save_data()
            self.refresh()
        else:
            messagebox.showwarning("Błąd", "Nie można dodać pustej notatki.")

    # Usuwa notatkę zaznaczoną na liście lub podświetloną
    def remove_note(self):
        idx = self.get_selected_index()
        if idx is not None:
            manager.get_current().remove_note(idx)
            self.last_added_index = None
            manager.save_data()
            self.refresh()

    # Wywołuje usuwanie wszystkich zrobionych notatek i odświeża widok
    def clean_done(self):
        manager.get_current().clean_done()
        manager.save_data()
        self.refresh()

    # Zamienia treść zaznaczonej notatki na tekst wpisany w pole edycji
    def edit_note(self):
        idx = self.get_selected_index()
        if idx is not None:
            new_text = self.entry.get().strip()
            if new_text:
                manager.get_current().edit_note(idx, new_text)
                self.entry.delete(0, tk.END)
                manager.save_data()
                self.refresh()

    # Zmienia status zaznaczonej notatki (zrobione/niezrobione)
    def toggle_done(self):
        idx = self.get_selected_index()
        if idx is not None:
            manager.get_current().toggle_done(idx)
            manager.save_data()
            self.refresh()

    # Ustawia tryb wyświetlania (wszystkie / tylko zrobione / tylko do zrobienia)
    def set_filter(self, mode):
        self.filter_mode = mode
        self.refresh()

    # Pobiera nazwę z pola wpisywania i tworzy nowy notatnik
    def add_notebook(self):
        name = self.entry.get().strip()
        if manager.add_notebook(name):
            self.entry.delete(0, tk.END)
            manager.save_data()
            self.refresh_notebook_menu()
            self.refresh()
        else:
            messagebox.showwarning("Błąd", "Nie można dodać notatnika")

    def remove_notebook_btn(self):
        current_name = manager.current
        answer = messagebox.askyesno("Potwierdzenie", f"Czy na pewno usunąć notatnik '{current_name}' i wszystkie jego notatki?")
        if answer:
            if manager.remove_notebook(current_name):
                self.refresh_notebook_menu()
                self.refresh()
            else:
                messagebox.showerror("Błąd", "Nie możesz usunąć ostatniego notatnika!")

    # Przełącza aplikację na wybrany z menu notatnik
    def switch_notebook(self, name):
        if manager.switch(name):
            self.nb_var.set(name)
            self.last_added_index = None
            self.refresh()

    # Główna funkcja: słucha głosu, pyta AI o intencję i wykonuje odpowiednią akcję
    def handle_voice_command(self):
        # Wizualna zmiana przycisku na czas słuchania użytkownika
        self.voice_btn.config(text="Słucham...", bg="green")
        self.root.update()

        # Pobranie tekstu z mikrofonu i przywrócenie wyglądu przycisku
        text = get_speech()
        print(">>> ROZPOZNANO:", text)
        self.voice_btn.config(text="Mów", bg="SystemButtonFace")

        if not text:
            return

        # Próba zamiany mowy na instrukcję JSON przez model LLM
        try:
            data = interpret_command(text)
            print("LLM zrozumiało:", data)
        except Exception as e:
            print(f"Błąd API: {e}")
            messagebox.showerror("Błąd połączenia", "Problem z połączeniem z AI.")
            return

        action = data.get("action")
        idx = data.get("id")
        query = data.get("query")
        final_idx = None

        # Ścieżka 1: Próba użycia bezpośredniego numeru ID od AI
        if idx is not None:
            try:
                final_idx = int(idx) - 1
            except:
                final_idx = None

        # Ścieżka 2: Jeśli brak ID, sprawdzenie czy zapytanie tekstowe jest liczbą lub szukanie tekstu
        if final_idx is None and query is not None:
            if str(query).isdigit():
                final_idx = int(query) - 1
            else:
                # Zamiana tekstu na indeks poprzez przeszukanie treści notatek
                final_idx = manager.find_note_by_text(query)

        # Wykonanie akcji dodania nowej notatki i zaznaczenie jej na liście
        if action == "add_note":
            content = data.get("text")
            if content and manager.get_current().add_note(content):
                self.last_added_index = len(manager.get_current().list_notes()) - 1

        # Usunięcie notatki na podstawie wyliczonego wcześniej indeksu
        elif action == "remove_note":
            if final_idx is not None:
                manager.get_current().remove_note(final_idx)
                self.last_added_index = None

        # Przełączenie statusu wykonania (zrobione/niezrobione)
        elif action == "toggle_done":
            if final_idx is not None:
                manager.get_current().toggle_done(final_idx)

        # Zmiana treści istniejącej notatki na nowy tekst od AI
        elif action == "edit_note":
            new_text = data.get("text") or data.get("new_text")
            if final_idx is not None and new_text:
                manager.get_current().edit_note(final_idx, new_text)

        # Zmiana aktualnie używanego notatnika na inny
        elif action == "switch_notebook":
            name = data.get("name") or data.get("query")
            if name and manager.switch(name):
                self.refresh_notebook_menu()

        # Utworzenie całkiem nowej listy (notatnika)
        elif action == "add_notebook":
            name = data.get("name") or data.get("query")
            if name and manager.add_notebook(name):
                self.refresh_notebook_menu()
                self.last_added_index = None

        # Zmiana trybu wyświetlania notatek (filtrowanie)
        elif action == "list_filter":
            self.set_filter(data.get("value", "all"))

        # Masowe usunięcie wszystkich notatek oznaczonych jako wykonane
        elif action == "clean_done":
            manager.get_current().clean_done()

        # Usuwanie notatnika głosowo
        elif action == "remove_notebook":
            target_name = data.get("name") or data.get("query") or manager.current
            answer = messagebox.askyesno("Potwierdzenie", f"Czy na pewno usunąć notatnik '{target_name}' i wszystkie jego notatki?")
            if answer:
                if manager.remove_notebook(target_name):
                    self.refresh_notebook_menu()
                else:
                    messagebox.showerror("Błąd", "Nie można usunąć tego notatnika (być może nie istnieje lub jest jedyny).")

        # Wyświetlenie pomocy
        elif action == "show_help":
            self.show_help()

        manager.save_data()
        self.refresh()