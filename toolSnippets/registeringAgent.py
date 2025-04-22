class AgentRegistry:
    def __init__(self):
        self.agents = {}
        
    def register_agent(self, name: str, run_function: callable):
        """Rekisteröi agentin suoritusfunktio."""
        self.agents[name] = run_function
        
    def get_agent(self, name: str) -> callable:
        """Hae agentin suoritusfunktio nimen perusteella."""
        return self.agents.get(name)

# Järjestelmän alustamisen yhteydessä
registry = AgentRegistry()
registry.register_agent("scheduler_agent", scheduler_agent.run)

# Sisällytä rekisteri toiminnon kontekstiin
action_context = ActionContext({
    'agent_registry': registry,
    # Muut jaetut resurssit...
})