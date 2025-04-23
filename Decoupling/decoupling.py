import os
import uuid
from dotenv import load_dotenv
from litellm import completion
from typing import Dict, List, Callable

# Ladataan ympäristömuuttujat .env-tiedostosta
load_dotenv()

# Haetaan OpenAI:n API-avain ympäristömuuttujista
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    # Heitetään virhe, jos API-avain puuttuu
    raise ValueError("API-avain puuttuu! Lisää se .env-tiedostoon tai tarkista polku.")

# Asetetaan API-avain litellm-kirjaston käyttöön ympäristömuuttujana
os.environ["OPENAI_API_KEY"] = api_key


# ActionContext-luokka injektiota varten (riippuvuuksien hallinta)
class ActionContext:
    def __init__(self, properties: Dict = None):
        # Jokaiselle kontekstille luodaan uniikki tunniste
        self.context_id = str(uuid.uuid4())
        # Tallennetaan annetut ominaisuudet
        self.properties = properties or {}

    def get(self, key: str, default=None):
        # Haetaan ominaisuus annetulla avaimella
        return self.properties.get(key, default)

    def get_memory(self):
        # Palautetaan muisti (jos se on määritelty)
        return self.properties.get("memory", None)


# Memory-luokka muistia (keskusteluhistoriaa) varten
class Memory:
    def __init__(self):
        # Lista, johon tallennetaan muistot
        self._memories = []

    def add_memory(self, mem_type: str, content: str):
        # Lisätään uusi muisti, jossa on tyyppi (esim. "user") ja sisältö
        self._memories.append({"type": mem_type, "content": content})

    def get_memories(self) -> List[Dict]:
        # Palautetaan kaikki muistot
        return self._memories


# LLM-funktio, joka integroi OpenAI:n GPT-mallin
def real_llm(prompt: str) -> str:
    # OpenAI:n Chat API vaatii "messages"-taulukon
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},  # Järjestelmäsanoma (ohjeistus mallille)
        {"role": "user", "content": prompt}  # Käyttäjän antama pyyntö
    ]
    # Kutsutaan litellm-kirjaston completion-metodia
    return completion(messages=messages, model="gpt-4", api_key=os.getenv("OPENAI_API_KEY"))

# Työkalu: Koodin laadun analysointi
def analyze_code_quality(action_context: ActionContext, code: str) -> str:
    memory = action_context.get_memory()  # Haetaan keskusteluhistoria
    development_context = []

    # Käydään läpi keskusteluhistoria ja lisätään relevantit tiedot
    for mem in memory.get_memories():
        if mem["type"] == "user":
            development_context.append(f"User: {mem['content']}")  # Käyttäjän viesti
        elif mem["type"] == "assistant" and "Here's the implementation" in mem["content"]:
            development_context.append(f"Implementation Decision: {mem['content']}")  # Assistentin päätökset

    # Luodaan kehotus koodin tarkasteluun
    review_prompt = f"""Review this code in the context of its development history:

Development History:
{'\n'.join(development_context)}

Current Implementation:
{code}

Analyze:
1. Does the implementation meet all stated requirements?
2. Are all constraints and considerations from the discussion addressed?
3. Have any requirements or constraints been overlooked?
4. What improvements could make the code better while staying within the discussed parameters?
"""
    generate_response = action_context.get("llm")  # Haetaan LLM-funktio kontekstista
    return generate_response(review_prompt)


# Työkalu: Päivitä tarkastelutilanne
def update_review_status(action_context: ActionContext, review_id: str, status: str) -> dict:
    auth_token = action_context.get("auth_token")  # Haetaan autentikointitoken
    if not auth_token:
        # Jos autentikointitoken puuttuu, heitetään virhe
        raise ValueError("Authentication token not found in context")

    # Simuloidaan API-vastausta
    return {"status": "updated", "review_id": review_id, "new_status": status}


# Agentti-luokka työkalujen ja kontekstien hallintaan
class Agent:
    def __init__(self, llm: Callable, tools: Dict[str, Callable]):
        # Tallennetaan LLM-funktio ja työkalut
        self.llm = llm
        self.tools = tools

    def run(self, user_input: str, memory: Memory, action_context_props: Dict = None):
        # Luodaan ActionContext, joka sisältää muistion ja muut ominaisuudet
        action_context = ActionContext({
            "memory": memory,
            "llm": self.llm,
            **(action_context_props or {})  # Lisätään mahdolliset lisäominaisuudet
        })

        print(f"Agent Input: {user_input}")
        while True:
            # Analysoi koodin laatu, jos käyttäjän syötteessä on sana "analyze"
            if "analyze" in user_input.lower():
                print("Analyzing code quality...")
                code = "def example():\n    return 'Hello, world!'"  # Esimerkkikoodi
                result = self.tools["analyze_code_quality"](action_context, code)
                print(f"Tool Output: {result}")
            # Päivitä tarkastelutilanne, jos käyttäjän syötteessä on sana "update"
            elif "update" in user_input.lower():
                print("Updating review status...")
                review_id = "12345"  # Esimerkinomainen tarkastelutunnus
                status = "approved"  # Päivitetty tila
                result = self.tools["update_review_status"](action_context, review_id, status)
                print(f"Tool Output: {result}")
            else:
                # Jos syöte ei vastaa mihinkään työkaluun
                print("No matching tool found for input.")
            break


# Muistin ja työkalujen asettaminen
memory = Memory()
memory.add_memory("user", "Can you review this code?")  # Käyttäjän pyyntö
memory.add_memory("assistant", "Here's the implementation: def example(): return 'Hello, world!'")  # Assistentin viesti

tools = {
    "analyze_code_quality": analyze_code_quality,  # Koodin analysointityökalu
    "update_review_status": update_review_status  # Tarkastelutilanteen päivitystyökalu
}

# Agentin suorittaminen
agent = Agent(llm=real_llm, tools=tools)
agent.run("Analyze the code quality", memory)  # Suoritetaan analyysi
agent.run("Update the review status", memory, action_context_props={"auth_token": "my_auth_token"})  # Päivitetään tarkastelutilanne