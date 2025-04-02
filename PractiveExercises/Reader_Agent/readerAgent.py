import os
import json
from dotenv import load_dotenv
from litellm import completion
from typing import List, Dict

# Lataa ympäristömuuttujat .env-tiedostosta
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Tarkista, että API-avain on asetettu
if not api_key:
    raise ValueError("API-avain puuttuu! Lisää se .env-tiedostoon.")

# Aseta API-avain ympäristömuuttujaksi LiteLLM:ää varten
os.environ["OPENAI_API_KEY"] = api_key


# Funktio: Listaa kaikki tiedostot ja kansiot annetussa hakemistossa
def list_files(directory: str = ".") -> List[str]:
    """
    Listaa kaikki tiedostot ja kansiot annetussa hakemistossa.

    Args:
        directory (str): Hakemisto, jonka sisältö listataan. Oletuksena nykyinen hakemisto.

    Returns:
        List[str]: Lista tiedostojen ja kansioiden poluista.
    """
    file_list = []
    for root, dirs, files in os.walk(directory):
        for name in files:
            file_list.append(os.path.join(root, name))
    return file_list


# Funktio: Lue yksittäisen tiedoston sisältö
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
        return f"Virhe: {file_name} ei löydy."
    except Exception as e:
        return f"Virhe: {str(e)}"


# Funktio: Lue kaikki tiedostot annetusta hakemistosta
def read_folder(folder_path: str) -> Dict[str, str]:
    """
    Lue kaikki tiedostot annetusta hakemistosta ja palauta niiden sisällöt.

    Args:
        folder_path (str): Hakemisto, jonka tiedostot luetaan.

    Returns:
        Dict[str, str]: Sanakirja, jossa avaimina tiedostopolut ja arvoina tiedostojen sisällöt.
    """
    contents = {}
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            contents[file_path] = read_file(file_path)
    return contents


# Funktio: Lopeta agentin toiminta ja tulosta viesti
def terminate(message: str) -> None:
    """
    Lopeta agentin toiminta ja tulosta viesti.

    Args:
        message (str): Lopetusviesti, joka tulostetaan.
    """
    print(f"Lopetusviesti: {message}")


# Työkalujen määrittely: Funktiot, joita agentti voi käyttää
tool_functions = {
    "list_files": list_files,
    "read_file": read_file,
    "read_folder": read_folder,
    "terminate": terminate,
}

# Työkalujen kuvaus: Määritellään, miten LLM voi käyttää työkaluja
tools = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "Palauttaa listan hakemiston tiedostoista ja kansioista.",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string"}
                },
                "required": ["directory"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Lukee annetun tiedoston sisällön.",
            "parameters": {
                "type": "object",
                "properties": {"file_name": {"type": "string"}},
                "required": ["file_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_folder",
            "description": "Lukee kaikki tiedostot annetussa kansiossa ja palauttaa niiden sisällöt.",
            "parameters": {
                "type": "object",
                "properties": {
                    "folder_path": {"type": "string"}
                },
                "required": ["folder_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "terminate",
            "description": "Lopettaa keskustelun ja tulostaa annetun viestin.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"}
                },
                "required": ["message"]
            }
        }
    }
]

# Agentin säännöt: Ohjeet LLM:lle, miten työkaluja käytetään
agent_rules = [{
    "role": "system",
    "content": """
Olet AI-agentti, joka voi suorittaa tehtäviä käyttäen käytettävissä olevia työkaluja.
Voit listata tiedostoja, lukea yksittäisiä tiedostoja ja lukea koko kansioiden sisällön.
Jos käyttäjä pyytää tiedostoihin liittyvää tietoa, listaa ensin hakemiston sisältö ennen tiedostojen lukemista.

Kun tehtävä on suoritettu, lopeta keskustelu käyttämällä 'terminate' -työkalua.
"""
}]

# Alustetaan agentti
iterations = 0  # Iteraatioiden laskuri
max_iterations = 10  # Maksimimäärä iteraatioita ennen automaattista lopetusta

# Pyydä käyttäjältä tehtävä
user_task = input("Mitä haluat minun tekevän? ")

# Alustetaan keskusteluhistoria
memory = [{"role": "user", "content": user_task}]

# Agentin pääsilmukka
while iterations < max_iterations:
    # Päivitä viestit agentin säännöillä ja keskusteluhistorialla
    messages = agent_rules + memory

    # Lähetä pyyntö LLM:lle
    response = completion(
        model="openai/gpt-4o",
        messages=messages,
        tools=tools,
        max_tokens=1024
    )

    # Tarkista, palauttaako LLM työkalukutsun
    if response.choices[0].message.tool_calls:
        tool = response.choices[0].message.tool_calls[0]
        tool_name = tool.function.name
        tool_args = json.loads(tool.function.arguments)

        # Luo toiminto-objekti
        action = {
            "tool_name": tool_name,
            "args": tool_args
        }

        # Suorita työkalu tai lopeta, jos 'terminate' kutsutaan
        if tool_name == "terminate":
            print(f"Lopetusviesti: {tool_args['message']}")
            break
        elif tool_name in tool_functions:
            try:
                # Suorita työkalu ja tallenna tulos
                result = {"result": tool_functions[tool_name](**tool_args)}
            except Exception as e:
                # Käsittele virhe työkalun suorituksessa
                result = {"error": f"Virhe suorituksessa {tool_name}: {str(e)}"}
        else:
            # Tuntematon työkalu
            result = {"error": f"Tuntematon työkalu: {tool_name}"}

        # Tulosta toiminnon tulos
        print(f"Suoritetaan: {tool_name} parametreilla {tool_args}")
        print(f"Tulos: {result}")

        # Päivitä keskusteluhistoria
        memory.extend([
            {"role": "assistant", "content": json.dumps(action)},
            {"role": "user", "content": json.dumps(result)}
        ])
    else:
        # Jos LLM ei palauta työkalukutsua, tulosta sen vastaus
        result = response.choices[0].message.content
        print(f"Vastaus: {result}")
        break

    # Päivitä iterointilaskuri
    iterations += 1