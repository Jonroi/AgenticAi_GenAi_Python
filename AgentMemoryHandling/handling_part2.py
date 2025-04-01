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


# Alustetaan keskusteluhistoria, jossa määritellään avustajan rooli ja käyttäjän pyyntö
messages = [
    {
        "role": "system",
        "content": "Olet asiantunteva ohjelmistoinsinööri, joka suosii funktionaalista ohjelmointia.",
    },
    {
        "role": "user",
        "content": "Kirjoita funktio, joka vaihtaa sanakirjan avaimet ja arvot keskenään.",
    },
]

# Lähetetään ensimmäinen pyyntö LLM:lle ja tulostetaan sen vastaus
response = generate_response(messages)
print(response)

# Päivitetään keskusteluhistoria lisäämällä avustajan vastaus ja uusi käyttäjän pyyntö
# Tämä antaa LLM:lle "muistin" edellisestä vuorovaikutuksesta
messages = [
    {
        "role": "system",
        "content": "Olet asiantunteva ohjelmistoinsinööri, joka suosii funktionaalista ohjelmointia.",
    },
    {
        "role": "user",
        "content": "Kirjoita funktio, joka vaihtaa sanakirjan avaimet ja arvot keskenään.",
    },
    # Lisätään avustajan vastaus keskusteluhistoriaan
    {"role": "assistant", "content": response},
    # Käyttäjä pyytää päivittämään funktion lisäämällä dokumentaation
    {"role": "user", "content": "Päivitä funktio lisäämällä dokumentaatio."},
]

# Lähetetään päivitetty keskusteluhistoria LLM:lle ja tulostetaan sen vastaus
response = generate_response(messages)
print(response)