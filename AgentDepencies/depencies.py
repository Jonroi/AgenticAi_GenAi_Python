import os
import uuid
import requests
from inspect import signature, Parameter
from typing import Dict, Any, Callable, List, get_type_hints
from dotenv import load_dotenv

# Lataa ympäristömuuttujat .env-tiedostosta
load_dotenv()

# Hae API-avain ympäristömuuttujista
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API-avain puuttuu! Lisää se .env-tiedostoon.")

# Aseta API-avain ympäristömuuttujaksi
os.environ["OPENAI_API_KEY"] = api_key


# ActionContext-luokka injektiota varten
class ActionContext:
    def __init__(self, properties: Dict = None):
        self.context_id = str(uuid.uuid4())
        self.properties = properties or {}

    def get(self, key: str, default=None):
        return self.properties.get(key, default)


# Ympäristö, joka käsittelee automaattisen riippuvuuksien injektion
class PythonEnvironment:
    def execute_action(self, action_context: ActionContext, action: Callable, args: Dict) -> Dict:
        """Suorittaa toiminnon automaattisella riippuvuuksien injektiolla."""
        try:
            # Kopioidaan args, jotta alkuperäinen pysyy muuttumattomana
            args_copy = args.copy()

            # Tarkistetaan, tarvitseeko toiminto action_contextin
            if self._has_named_parameter(action, "action_context"):
                args_copy["action_context"] = action_context

            # Lisätään ActionContextin ominaisuudet, jotka vastaavat _-prefiksillä alkavia parametreja
            for key, value in action_context.properties.items():
                param_name = f"_{key}"
                if self._has_named_parameter(action, param_name):
                    args_copy[param_name] = value

            # Suoritetaan toiminto injektoiduilla riippuvuuksilla
            result = action(**args_copy)
            return {"tool_executed": True, "result": result}
        except Exception as e:
            return {"tool_executed": False, "error": str(e)}

    @staticmethod
    def _has_named_parameter(func: Callable, name: str) -> bool:
        """Tarkistaa, onko funktiolla tietty nimetty parametri."""
        return name in signature(func).parameters


# Työkalujen rekisteröintijärjestelmä
def register_tool(description: str = None):
    """Koristeluohjelma työkalujen rekisteröintiin."""
    def wrapper(func: Callable):
        func.metadata = get_tool_metadata(func, description=description)
        return func
    return wrapper


def get_tool_metadata(func: Callable, description: str = None) -> Dict:
    """Luo metatiedot työkalusta, ohittaen erityisparametrit."""
    sig = signature(func)
    type_hints = get_type_hints(func)

    args_schema = {
        "type": "object",
        "properties": {},
        "required": []
    }

    for param_name, param in sig.parameters.items():
        # Ohitetaan erityisparametrit, kuten action_context ja _-prefiksillä alkavat
        if param_name == "action_context" or param_name.startswith("_"):
            continue

        # Lisätään normaalit parametrit skeemaan
        param_type = type_hints.get(param_name, str)
        args_schema["properties"][param_name] = {"type": "string"}
        if param.default == Parameter.empty:
            args_schema["required"].append(param_name)

    return {
        "name": func.__name__,
        "description": description or func.__doc__,
        "parameters": args_schema
    }


# Esimerkki: Koodin laadun analysointi
@register_tool(description="Analysoi koodin laatua")
def analyze_code_quality(action_context: ActionContext, code: str) -> str:
    """Analysoi koodin laadun keskusteluhistorian perusteella."""
    development_context = action_context.get("memory", [])
    context_str = "\n".join(development_context)
    return f"Keskusteluhistoria:\n{context_str}\nAnalysoitava koodi:\n{code}"


# Esimerkki: Päivitä käyttäjän asetukset
@register_tool(description="Päivitä käyttäjän asetukset järjestelmässä")
def update_settings(action_context: ActionContext, setting_name: str, new_value: str, _auth_token: str, _user_config: dict) -> dict:
    """Päivittää käyttäjän asetukset ulkoisessa järjestelmässä."""
    headers = {"Authorization": f"Bearer {_auth_token}"}
    if setting_name not in _user_config["allowed_settings"]:
        raise ValueError(f"Asetusta {setting_name} ei sallita.")
    response = requests.post(
        "https://api.example.com/settings",
        headers=headers,
        json={"setting": setting_name, "value": new_value}
    )
    return {"updated": True, "setting": setting_name}


# Agenttiluokka, joka käsittelee toimintoja
class Agent:
    def __init__(self, environment: PythonEnvironment, tools: Dict[str, Callable]):
        self.environment = environment
        self.tools = tools

    def run(self, tool_name: str, args: Dict, action_context: ActionContext):
        """Suorittaa annetun työkalun."""
        tool = self.tools.get(tool_name)
        if not tool:
            return {"error": f"Työkalua {tool_name} ei löytynyt."}
        return self.environment.execute_action(action_context, tool, args)


# Esimerkinomainen käyttö
if __name__ == "__main__":
    # Luodaan ActionContext ja asetetaan ominaisuuksia
    action_context = ActionContext({
        "memory": ["Käyttäjä pyysi analysoimaan koodin."],
        "auth_token": "securetoken123",
        "user_config": {"allowed_settings": ["theme", "notifications"]}
    })

    # Rekisteröidään työkalut
    tools = {
        "analyze_code_quality": analyze_code_quality,
        "update_settings": update_settings
    }

    # Luodaan ympäristö ja agentti
    environment = PythonEnvironment()
    agent = Agent(environment, tools)

    # Suoritetaan työkaluja
    result1 = agent.run("analyze_code_quality", {"code": "def example(): return 'Hello, world!'"}, action_context)
    print("Analyysi tulos:", result1)

    result2 = agent.run("update_settings", {"setting_name": "theme", "new_value": "dark"}, action_context)
    print("Asetusten päivitys tulos:", result2)