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
    Mocked ActionContext for demonstration purposes.
    Replace with the actual implementation in your system.
    """
    def get(self, key: str, default=None):
        return default

    def get_memory(self):
        return Memory()


class Memory:
    """
    Mocked Memory class for demonstration purposes.
    Replace with the actual implementation in your system.
    """
    def add_memory(self, memory: Dict[str, Any]):
        print(f"Memory added: {memory}")


class Prompt:
    """
    Mocked Prompt class for demonstration purposes.
    Replace with the actual implementation in your system.
    """
    def __init__(self, messages: List[Dict[str, Any]]):
        self.messages = messages


class Capability:
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
    def __init__(self):
        super().__init__(
            name="Time Awareness",
            description="Allows the agent to be aware of time"
        )
        
    def init(self, agent, action_context: ActionContext) -> dict:
        """Set up time awareness at the start of agent execution."""
        time_zone_name = action_context.get("time_zone", "America/Chicago")
        timezone = ZoneInfo(time_zone_name)
        
        current_time = datetime.now(timezone)
        iso_time = current_time.strftime("%Y-%m-%dT%H:%M:%S%z")
        human_time = current_time.strftime("%H:%M %A, %B %d, %Y")
        
        memory = action_context.get_memory()
        memory.add_memory({
            "type": "system",
            "content": f"""Right now, it is {human_time} (ISO: {iso_time}).
            You are in the {time_zone_name} timezone.
            Please consider the day/time, if relevant, when responding."""
        })
        
    def process_prompt(self, agent, action_context: ActionContext, 
                       prompt: Prompt) -> Prompt:
        """Update time information in each prompt."""
        time_zone_name = action_context.get("time_zone", "America/Chicago")
        current_time = datetime.now(ZoneInfo(time_zone_name))
        
        system_msg = (f"Current time: "
                      f"{current_time.strftime('%H:%M %A, %B %d, %Y')} "
                      f"({time_zone_name})\n\n")
        
        messages = prompt.messages
        if messages and messages[0]["role"] == "system":
            messages[0]["content"] = system_msg + messages[0]["content"]
        else:
            messages.insert(0, {
                "role": "system",
                "content": system_msg
            })
            
        return Prompt(messages=messages)


class Agent:
    """
    Mocked Agent class for demonstration purposes.
    Replace with the actual implementation in your system.
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
        action_context = ActionContext()
        for capability in self.capabilities:
            capability.init(self, action_context)
        print(f"Agent running with input: {user_input}")


# Example usage
if __name__ == "__main__":
    agent = Agent(
        goals=["Complete the assigned task"],
        agent_language=None,
        action_registry=None,
        generate_response=None,
        environment=None,
        capabilities=[TimeAwareCapability()]
    )
    agent.run("What time is it?")