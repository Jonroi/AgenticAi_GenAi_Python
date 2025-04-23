from typing import List, Dict, Any
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

class ActionContext:
    """
    Mockattu ActionContext-luokka demonstraatiota varten.
    Korvaa tämä järjestelmän varsinaisella implementaatiolla.
    """
    def __init__(self):
        self.memory = Memory()
        self.action_registry = ActionRegistry()

    def get_memory(self):
        return self.memory

    def get_action_registry(self):
        return self.action_registry


class Memory:
    """
    Mockattu Memory-luokka demonstraatiota varten.
    Korvaa tämä järjestelmän varsinaisella implementaatiolla.
    """
    def __init__(self):
        self.items = []

    def add_memory(self, memory: Dict[str, Any]):
        self.items.append(memory)
        print(f"Muistiin lisätty: {memory}")


class ActionRegistry:
    """
    Mockattu ActionRegistry-luokka demonstraatiota varten.
    Korvaa tämä järjestelmän varsinaisella implementaatiolla.
    """
    def __init__(self):
        self.actions = [
            {"name": "validate_data", "description": "Tarkista datan eheys ja muoto."},
            {"name": "analyze_data", "description": "Suorita perusanalyysi datasta."},
            {"name": "find_patterns", "description": "Tunnista datasta kaavoja ja trendejä."},
            {"name": "create_visualization", "description": "Luo kaavioita ja visuaalisia esityksiä."},
            {"name": "generate_report", "description": "Laadi raportti löydöksistä."},
        ]

    def get_actions(self):
        return [Action(name=action["name"], description=action["description"]) for action in self.actions]


class Action:
    """
    Toimintoa edustava luokka toimintarekisterissä.
    """
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description


class Capability:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def init(self, agent, action_context: ActionContext) -> dict:
        pass


class PlanFirstCapability(Capability):
    """
    Kyvykkyys, joka edellyttää suunnittelua ennen agentin suoritusta.
    """
    def __init__(self, plan_memory_type="system", track_progress=False):
        super().__init__(
            name="Plan First Capability",
            description="Agentti luo aina suunnitelman ja lisää sen muistiin."
        )
        self.plan_memory_type = plan_memory_type
        self.first_call = True
        self.track_progress = track_progress

    def init(self, agent, action_context: ActionContext):
        """
        Alusta suunnitelma, kun agentti käynnistyy.
        """
        if self.first_call:
            self.first_call = False

            # Luo suunnitelma
            plan = create_plan(
                action_context=action_context,
                memory=action_context.get_memory(),
                action_registry=action_context.get_action_registry()
            )

            # Lisää suunnitelma muistiin
            action_context.get_memory().add_memory({
                "type": self.plan_memory_type,
                "content": "Noudata huolellisesti näitä ohjeita tehtävän suorittamiseksi:\n" + plan
            })


def create_plan(action_context: ActionContext, memory: Memory, action_registry: ActionRegistry) -> str:
    """
    Luo yksityiskohtainen suunnitelma agentille tehtävän ja käytettävissä olevien työkalujen perusteella.
    """
    # Hanki työkalujen kuvaukset
    tool_descriptions = "\n".join(
        f"- {action.name}: {action.description}"
        for action in action_registry.get_actions()
    )

    # Hanki asiaankuuluva muistisisältö
    memory_content = "\n".join(
        f"{m['type']}: {m['content']}"
        for m in memory.items
        if m['type'] in ['user', 'system']
    )

    # Rakenna kehote
    prompt = f"""Muistin tehtävän ja käytettävissä olevien työkalujen perusteella, luo yksityiskohtainen suunnitelma.
Ajattele tämä vaihe vaiheelta:

1. Tunnista ensin tehtävän keskeiset osat
2. Harkitse, mitä työkaluja on käytettävissä
3. Jaa tehtävä loogisiin vaiheisiin
4. Jokaisessa vaiheessa määritä:
   - Mitä pitää tehdä
   - Mitä työkalua/työkaluja käytetään
   - Mitä tietoa tarvitaan
   - Mikä on odotettu lopputulos

Kirjoita suunnitelmasi selkeinä, numeroituina vaiheina. Jokainen vaihe on oltava tarkka ja toteutettavissa.

Käytettävissä olevat työkalut:
{tool_descriptions}

Tehtäväkonteksti muistista:
{memory_content}

Luo suunnitelma, joka suorittaa tämän tehtävän tehokkaasti."""

    # Mockattu LLM-vastaus
    return prompt_llm(action_context=action_context, prompt=prompt)


def prompt_llm(action_context: ActionContext, prompt: str) -> str:
    """
    Mockattu funktio, joka simuloi LLM-vastausta. Korvaa tämä LLM-API-kutsulla.
    """
    print(f"Kehote lähetetty LLM:lle:\n{prompt}")
    return """Plan for Sales Data Analysis:

1. Tietojen validointi
   - Työkalu: validate_data()
   - Tarkista tietojen eheys ja muoto
   - Varmista, että kaikki tarvittavat kentät ovat läsnä
   - Odotettu: Vahvistus datasetin kelvollisuudesta

2. Alkuanalyysi
   - Työkalu: analyze_data()
   - Laske keskeiset mittarit (liikevaihto, kasvu)
   - Luo yhteenvetotilastoja
   - Odotettu: Perustilastollinen yleiskuva

3. Trendi-identifikaatio
   - Työkalu: find_patterns()
   - Etsi kausiluonteisia kaavoja
   - Tunnista myyntitrendit
   - Odotettu: Lista merkittävistä trendeistä

4. Visualisointi
   - Työkalu: create_visualization()
   - Luo asiaankuuluvia kaavioita
   - Korosta keskeiset löydökset
   - Odotettu: Selkeät visuaaliset esitykset

5. Raportin luonti
   - Työkalu: generate_report()
   - Koosta löydökset
   - Sisällytä visualisoinnit
   - Odotettu: Kattava raportti"""


class Agent:
    """
    Mockattu Agent-luokka demonstraatiota varten.
    Korvaa tämä järjestelmän varsinaisella implementaatiolla.
    """
    def __init__(self, goals: List[str], capabilities: List[Capability]):
        self.goals = goals
        self.capabilities = capabilities

    def run(self, user_input: str):
        """
        Suorita agentti annetulla syötteellä.
        """
        action_context = ActionContext()
        for capability in self.capabilities:
            capability.init(self, action_context)
        print(f"Agentti suorittaa syötteellä: {user_input}")


# Esimerkkikäyttö
if __name__ == "__main__":
    agent = Agent(
        goals=["Analysoi myyntidata ja luo raportti"],
        capabilities=[PlanFirstCapability(track_progress=True)]
    )
    agent.run("Analysoi meidän Q4:n myyntidata ja luo raportti")