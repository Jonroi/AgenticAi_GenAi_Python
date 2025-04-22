@register_tool()
def hand_off_to_agent(action_context: ActionContext, 
                      agent_name: str, 
                      task: str) -> dict:
    """Siirrä hallinta toiselle agentille ja jaa muisti."""
    agent_registry = action_context.get_agent_registry()
    agent_run = agent_registry.get_agent(agent_name)
    
    # Hae nykyinen muisti siirtoa varten
    current_memory = action_context.get_memory()
    
    # Suorita agentti olemassa olevalla muistilla
    result_memory = agent_run(
        user_input=task,
        memory=current_memory  # Välitä olemassa oleva muisti
    )
    
    return {
        "result": result_memory.items[-1].get("content", "Ei tulosta"),
        "memory_id": id(result_memory)
    }