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
            "Olet pelisivuston Alpotti niminen avustaja, kerrot kävijöille tietoja pelistä, sen sisällöstä ja hahmoista\n"
            "Tiedosto on nimeltään 'alpotti.json', ja sen sisältö on tallennettu muistiin.\n"
            "Vastaa aina käyttäjän kysymyksiin tiedoston sisällön perusteella."
        ),
    }
]

# Lue automaattisesti alpotti.json-tiedoston sisältö
selected_file = "alpotti.json"
file_content = read_file(selected_file)

if "Error" in file_content:
    print(f"Tiedoston '{selected_file}' lukeminen epäonnistui: {file_content}")
    exit()

# Päivitä keskusteluhistoria tiedoston sisällöllä
messages.append({"role": "user", "content": f"Lue tiedoston '{selected_file}' sisältö."})
messages.append({"role": "assistant", "content": f"Tiedoston '{selected_file}' sisältö on tallennettu muistiin."})

# Kysytään käyttäjältä, mitä hän haluaa tietää tiedostosta
while True:
    question = input("\nKäyttäjä: Kirjoita mitä haluat tietää Altzone pelistä: ").strip()
    if question.lower() == "exit":
        print("Ohjelma lopetettu.")
        break

    # Lisää käyttäjän kysymys keskusteluhistoriaan
    messages.append({"role": "user", "content": f"Tiedoston '{selected_file}' sisältö: {file_content}\nKysymys: {question}"})

    # Lähetä kysymys LLM:lle ja tulosta vastaus
    response = generate_response(messages)
    print(f"Avustaja: {response}")

    # Päivitä keskusteluhistoria avustajan vastauksella
    messages.append({"role": "assistant", "content": response})