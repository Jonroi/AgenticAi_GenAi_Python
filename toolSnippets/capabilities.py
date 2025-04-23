class Capability:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def init(self, agent, action_context: ActionContext) -> dict:
        """Kutsutaan kerran, kun agentti aloittaa suorittamisen."""
        pass

    def start_agent_loop(self, agent, action_context: ActionContext) -> bool:
        """Kutsutaan jokaisen agenttikehän iteraation alussa."""
        return True

    def process_prompt(self, agent, action_context: ActionContext, 
                      prompt: Prompt) -> Prompt:
        """Kutsutaan juuri ennen kehotteen lähettämistä LLM:lle."""
        return prompt

    def process_response(self, agent, action_context: ActionContext, 
                        response: str) -> str:
        """Kutsutaan, kun LLM:n vastaus on saatu."""
        return response

    def process_action(self, agent, action_context: ActionContext, 
                      action: dict) -> dict:
        """Kutsutaan, kun vastaus on muunnettu toiminnoksi."""
        return action

    def process_result(self, agent, action_context: ActionContext,
                      response: str, action_def: Action,
                      action: dict, result: any) -> any:
        """Kutsutaan toiminnon suorittamisen jälkeen."""
        return result

    def process_new_memories(self, agent, action_context: ActionContext,
                           memory: Memory, response, result,
                           memories: List[dict]) -> List[dict]:
        """Kutsutaan, kun uusia muistoja lisätään."""
        return memories

    def end_agent_loop(self, agent, action_context: ActionContext):
        """Kutsutaan jokaisen agenttikehän iteraation lopussa."""
        pass

    def should_terminate(self, agent, action_context: ActionContext,
                        response: str) -> bool:
        """Kutsutaan tarkistamaan, tulisiko agentin lopettaa."""
        return False

    def terminate(self, agent, action_context: ActionContext) -> dict:
        """Kutsutaan, kun agentti suljetaan."""
        pass