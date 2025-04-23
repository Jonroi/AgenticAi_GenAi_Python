import os
from dotenv import load_dotenv
from litellm import completion
from typing import List, Dict

# Lataa ympäristömuuttujat .env-tiedostosta
load_dotenv()

# Hae API-avain ympäristömuuttujista
api_key = os.getenv("OPENAI_API_KEY")

# Tarkista, että API-avain on asetettu
if not api_key:
    raise ValueError("API-avain puuttuu! Lisää se .env-tiedostoon.")

# Aseta API-avain ympäristömuuttujaksi LiteLLM:ää varten
os.environ["OPENAI_API_KEY"] = api_key


def generate_response(messages: List[Dict]) -> str:
    """
    Lähetä viestihistoria LLM:lle ja palauta sen vastaus.

    Args:
        messages (List[Dict]): Lista viesteistä, jotka sisältävät käyttäjän ja avustajan vuorovaikutuksen.

    Returns:
        str: LLM:n tuottama vastaus viestihistorian perusteella.
    """
    response = completion(model="openai/gpt-4o", messages=messages, max_tokens=1024)
    return response.choices[0].message.content


def list_files_in_directory(directory: str = ".") -> List[str]:
    """
    Listaa kaikki tiedostot annetussa hakemistossa.

    Args:
        directory (str): Hakemisto, jonka tiedostot listataan. Oletuksena nykyinen hakemisto.

    Returns:
        List[str]: Lista tiedostonimistä hakemistossa.
    """
    try:
        return os.listdir(directory)
    except FileNotFoundError:
        return ["Error: Directory not found."]
    except PermissionError:
        return ["Error: Permission denied."]


def read_file(file_name: str) -> str:
    """
    Lue tiedoston sisältö.

    Args:
        file_name (str): Tiedoston nimi, joka luetaan.

    Returns:
        str: Tiedoston sisältö tai virheilmoitus.
    """
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return "Error: File not found."
    except PermissionError:
        return "Error: Permission denied."
    except Exception as e:
        return f"Error: {str(e)}"


# Alustetaan keskusteluhistoria, jossa määritellään avustajan rooli
messages = [
    {
        "role": "system",
        "content": (
            "Olet asiantunteva ohjelmistoinsinööri, joka voi suorittaa seuraavat toiminnot:\n"
            "- Listaa tiedostot hakemistossa (list_files_in_directory).\n"
            "- Lue tiedoston sisältö (read_file).\n"
            "Vastaa aina toimintamuodossa, esimerkiksi:\n"
            "```action\n{\"tool_name\": \"list_files_in_directory\", \"args\": {\"directory\": \".\"}}\n```"
        ),
    }
]

# Pääohjelman silmukka
while True:
    # Listaa tiedostot ja pyydä käyttäjää valitsemaan tiedosto
    print("\nHakemiston tiedostot:")
    files = list_files_in_directory()
    for idx, file_name in enumerate(files, start=1):
        print(f"{idx}. {file_name}")

    user_input = input("\nKäyttäjä: Valitse tiedoston numero tai kirjoita 'exit' lopettaaksesi: ").strip()
    if user_input.lower() == "exit":
        print("Ohjelma lopetettu.")
        break

    # Tarkista, onko syöte validi numero
    if user_input.isdigit():
        file_index = int(user_input) - 1
        if 0 <= file_index < len(files):
            selected_file = files[file_index]
            print(f"Valitsit tiedoston: {selected_file}")
        else:
            print("Virhe: Valitsemasi numero ei vastaa mitään tiedostoa.")
            continue
    else:
        print("Virhe: Anna tiedoston numero tai kirjoita 'exit'.")
        continue

    # Lue valitun tiedoston sisältö
    file_content = read_file(selected_file)
    if "Error" in file_content:
        print(f"Tiedoston '{selected_file}' lukeminen epäonnistui: {file_content}")
        continue

    # Päivitä keskusteluhistoria tiedoston sisällöllä
    messages.append({"role": "user", "content": f"Lue tiedoston '{selected_file}' sisältö."})
    messages.append({"role": "assistant", "content": f"Tiedoston '{selected_file}' sisältö on tallennettu muistiin."})

    print(f"Tiedoston '{selected_file}' sisältö on tallennettu muistiin.")

    # Kysytään käyttäjältä, mitä hän haluaa tietää tiedostosta
    while True:
        question = input("\nKäyttäjä: Mitä haluat tietää tästä tiedostosta? (Kirjoita 'back' palataksesi tiedoston valintaan): ").strip()
        if question.lower() == "back":
            print("Palataan tiedoston valintaan.")
            break

        # Lisää käyttäjän kysymys keskusteluhistoriaan
        messages.append({"role": "user", "content": f"Tiedoston '{selected_file}' sisältö: {file_content}\nKysymys: {question}"})

        # Lähetä kysymys LLM:lle ja tulosta vastaus
        response = generate_response(messages)
        print(f"Avustaja: {response}")

        # Päivitä keskusteluhistoria avustajan vastauksella
        messages.append({"role": "assistant", "content": response})