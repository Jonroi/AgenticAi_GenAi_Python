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


# Alustetaan keskusteluhistoria, jossa määritellään avustajan rooli ja käyttäjän pyyntö
messages = [
    {
        "role": "system",
        "content": (
            "Olet asiantunteva ohjelmistoinsinööri, joka voi suorittaa seuraavat toiminnot:\n"
            "- Listaa tiedostot hakemistossa (list_files_in_directory).\n"
            "- Kirjoita Python-funktioita ja lisää niihin dokumentaatio.\n"
            "Vastaa aina toimintamuodossa, esimerkiksi:\n"
            "```action\n{\"tool_name\": \"list_files_in_directory\", \"args\": {\"directory\": \".\"}}\n```"
        ),
    },
    {
        "role": "user",
        "content": "Listaa tämän kansion tiedostot.",
    },
]

# Lähetetään ensimmäinen pyyntö LLM:lle ja tulostetaan sen vastaus
response = generate_response(messages)
print("LLM:n vastaus:", response)

# Tarkistetaan, haluaako LLM käyttää tiedostojen listaustyökalua
if "list_files_in_directory" in response:
    # Parsitaan hakemisto, jos se on määritelty
    directory = "."
    if "\"directory\"" in response:
        start = response.find("\"directory\"") + len("\"directory\":") + 1
        end = response.find("}", start)
        directory = response[start:end].strip().strip("\"")

    # Suoritetaan tiedostojen listaus
    files = list_files_in_directory(directory)
    print("Hakemiston tiedostot:", files)

    # Päivitetään keskusteluhistoria tiedostojen listauksen tuloksella
    messages.append({"role": "assistant", "content": response})
    messages.append({"role": "user", "content": str(files)})

# Lähetetään päivitetty keskusteluhistoria LLM:lle ja tulostetaan sen vastaus
response = generate_response(messages)
print("LLM:n päivitetty vastaus:", response)