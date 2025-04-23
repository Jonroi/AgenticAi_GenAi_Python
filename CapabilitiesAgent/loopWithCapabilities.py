from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List, Dict, Any
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


class ActionContext:
    """
    Toimintakonteksti-luokka (mockattu).
    Tämän voi korvata järjestelmän todellisella implementaatiolla.
    """
    def get(self, key: str, default=None):
        return default

    def get_memory(self):
        return Memory()


class Memory:
    """
    Muisti-luokka (mockattu).
    Tämän voi korvata järjestelmän todellisella implementaatiolla.
    """
    def add_memory(self, memory: Dict[str, Any]):
        # Tulostetaan, mitä muistiin lisätään
        print(f"Muistiin lisätty: {memory}")


class Prompt:
    """
    Prompt-luokka (mockattu).
    Tämän voi korvata järjestelmän todellisella implementaatiolla.
    """
    def __init__(self, messages: List[Dict[str, Any]]):
        self.messages = messages


class Capability:
    """
    Kyvykkyys-luokka, jota käytetään agentin toiminnan laajentamiseen.
    """
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def init(self, agent, action_context: ActionContext) -> dict:
        pass

    def start_agent_loop(self, agent, action_context: ActionContext) -> bool:
        return True

    def process_prompt(self, agent, action_context: ActionContext, 
                       prompt: Prompt) -> Prompt:
        return prompt

    def process_response(self, agent, action_context: ActionContext, 
                         response: str) -> str:
        return response

    def process_action(self, agent, action_context: ActionContext, 
                       action: dict) -> dict:
        return action

    def process_result(self, agent, action_context: ActionContext, response: str, 
                       action_def: Any, action: dict, result: Any) -> Any:
        return result

    def process_new_memories(self, agent, action_context: ActionContext,
                             memory: Memory, response, result,
                             memories: List[dict]) -> List[dict]:
        return memories

    def end_agent_loop(self, agent, action_context: ActionContext):
        pass

    def should_terminate(self, agent, action_context: ActionContext,
                         response: str) -> bool:
        return False

    def terminate(self, agent, action_context: ActionContext) -> dict:
        pass


class TimeAwareCapability(Capability):
    """
    Kyvykkyys, joka tekee agentista ajan suhteen tietoiseksi.
    """
    def __init__(self):
        super().__init__(
            name="Aikatietoisuus",
            description="Mahdollistaa ajan huomioimisen agentissa"
        )
        
    def init(self, agent, action_context: ActionContext) -> dict:
        """
        Asetetaan ajan suhteen tietoisuus agentin suorituksen alussa.
        """
        time_zone_name = action_context.get("time_zone", "America/Chicago")
        timezone = ZoneInfo(time_zone_name)
        
        # Haetaan nykyinen aika ja muotoillaan se
        current_time = datetime.now(timezone)
        iso_time = current_time.strftime("%Y-%m-%dT%H:%M:%S%z")
        human_time = current_time.strftime("%H:%M %A, %B %d, %Y")
        
        # Lisätään aika muistiin
        memory = action_context.get_memory()
        memory.add_memory({
            "type": "system",
            "content": f"""Nyt on {human_time} (ISO: {iso_time}).
            Olet {time_zone_name} aikavyöhykkeellä.
            Ota päivä/aika huomioon, jos se on relevanttia."""
        })
        
    def process_prompt(self, agent, action_context: ActionContext, 
                       prompt: Prompt) -> Prompt:
        """
        Päivitetään ajan tietoisuus jokaiseen promptiin.
        """
        time_zone_name = action_context.get("time_zone", "America/Chicago")
        current_time = datetime.now(ZoneInfo(time_zone_name))
        
        # Luodaan järjestelmän viesti, jossa kerrotaan nykyinen aika
        system_msg = (f"Nykyinen aika: "
                      f"{current_time.strftime('%H:%M %A, %B %d, %Y')} "
                      f"({time_zone_name})\n\n")
        
        messages = prompt.messages
        if messages and messages[0]["role"] == "system":
            # Päivitetään olemassa oleva järjestelmän viesti
            messages[0]["content"] = system_msg + messages[0]["content"]
        else:
            # Lisätään uusi järjestelmän viesti
            messages.insert(0, {
                "role": "system",
                "content": system_msg
            })
            
        return Prompt(messages=messages)


class Agent:
    """
    Agentti-luokka (mockattu).
    Tämän voi korvata järjestelmän todellisella implementaatiolla.
    """
    def __init__(self, goals, agent_language, action_registry, generate_response,
                 environment, capabilities=None, max_iterations=10, 
                 max_duration_seconds=180):
        self.goals = goals
        self.generate_response = generate_response
        self.agent_language = agent_language
        self.actions = action_registry
        self.environment = environment
        self.capabilities = capabilities or []
        self.max_iterations = max_iterations
        self.max_duration_seconds = max_duration_seconds

    def run(self, user_input: str):
        """
        Suorita agentin toiminto käyttäjän syötteen perusteella.
        """
        action_context = ActionContext()
        for capability in self.capabilities:
            capability.init(self, action_context)
        print(f"Agentti suorittaa seuraavalla syötteellä: {user_input}")


# Esimerkki käytöstä
if __name__ == "__main__":
    agent = Agent(
        goals=["Suorita annettu tehtävä"],
        agent_language=None,
        action_registry=None,
        generate_response=None,
        environment=None,
        capabilities=[TimeAwareCapability()]
    )
    agent.run("Mikä on nykyinen aika?")