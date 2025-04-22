@register_tool()
def call_agent(action_context: ActionContext, 
               agent_name: str, 
               task: str) -> dict:
    # Hae agenttirekisteri toimintakontekstista
    agent_registry = action_context.get_agent_registry()

    # Hae kutsuttava agentti agenttirekisteristä
    agent_run = agent_registry.get_agent(agent_name)

    # Luo uusi muisti kutsuttavaa agenttia varten
    invoked_memory = Memory()

    # Suorita agentti ja tallenna tulosmuisti
    result_memory = agent_run(
        user_input=task,  # Käyttäjän antama tehtävä
        memory=invoked_memory  # Tyhjä muisti agentin käyttöön
    )

    # Palauta vain viimeisin muistisisältö tuloksena
    return {
        "result": result_memory.items[-1].get("content", "No result")  # Viimeisin sisältö tai oletusviesti
    }