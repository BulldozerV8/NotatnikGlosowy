import json
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("UWAGA: Brak klucza API. Utwórz plik .env lub wpisz klucz w kodzie.")
    api_key = "BRAK_KLUCZA"

client = Groq(api_key=api_key)


SYSTEM_PROMPT = """
Jesteś mózgiem notatnika. Interpretujesz intencje użytkownika i zwracasz TYLKO JSON.

ZASADY POLA 'id' I 'query':
- Jeśli użytkownik mówi o numerze (np. "pierwszą", "notatkę numer 2", "tę drugą"), wpisz cyfrę do pola "id".
- Jeśli użytkownik opisuje treść (np. "tę o zakupach", "notatkę z dentyście"), wpisz opis do pola "query".

MOŻLIWE AKCJE:
1. add_note (tekst) - dodanie notatki
2. remove_note (id lub tekst) - usunięcie
3. edit_note (id, nowy_tekst) - zmiana treści
4. toggle_done (id lub tekst) - oznaczenie jako wykonane
5. add_notebook (nazwa) - dodanie notatnika
6. switch_notebook (nazwa) - zmiana folderu/notatnika
7. list_filter (value: "done", "todo" lub "all") - filtrowanie 
8. clean_done (bez parametrów) - usuniecie zrobionych
9. remove_notebook (nazwa) - usunięcie notatnika (folderu)
10. show_help (bez parametrów) - wyświetlenie pomocy

PRZYKŁADY:
"Przypomnij mi jutro o dentyście" -> {"action": "add_note", "text": "dentysta jutro"}
"Wywal to o zakupach" -> {"action": "remove_note", "query": "zakupy"}
"Zaznacz mleko jako zrobione" -> {"action": "toggle_done", "query": "mleko"}
"Pokaż tylko te co zrobiłem" -> {"action": "list_filter", "value": "done"}
"Usuń notatnik praca" -> {"action": "remove_notebook", "name": "praca"}
"Co mogę powiedzieć" -> {"action": "show_help"}

ZASADY:
- Zwracaj tylko czysty JSON.
- Jeśli nie jesteś pewien ID, w polu "query" wpisz słowo kluczowe.
"""

# Wysyła tekst do modelu Llama 3.3, aby otrzymać techniczny JSON z instrukcją
def interpret_command(text: str):
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
        response_format={"type": "json_object"}
    )

    return json.loads(completion.choices[0].message.content)